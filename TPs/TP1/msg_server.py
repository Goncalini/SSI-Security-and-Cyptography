import asyncio
import os
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh, padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import validator, utils

conn_cnt = 0
conn_port = 8443
max_msg_size = 9999

# Parâmetros para a geração de chaves Diffie-Hellman dado no enunciado
g = 2
p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
parameters = dh.DHParameterNumbers(p, g).parameters()

# Dicionario #{UID, [(msg1, flag), (msg2, flag), ...]}
queues = {}

def mkpair(x, y):
    """produz uma byte-string contendo o tuplo '(x,y)' ('x' e 'y' são byte-strings)"""
    len_x = len(x)
    len_x_bytes = len_x.to_bytes(2, "little")
    return len_x_bytes + x + y


def unpair(xy):
    """extrai componentes de um par codificado com 'mkpair'"""
    len_x = int.from_bytes(xy[:2], "little")
    x = xy[2 : len_x + 2]
    y = xy[len_x + 2 :]
    return x, y

class ServerWorker(object):
    """ Classe que implementa a funcionalidade do SERVIDOR. """
    def __init__(self, cnt, addr=None):
        """ Construtor da classe. """
        self.id = cnt
        self.addr = addr
        self.msg_cnt = 0

        self.uid = None
        self.queue = None

        self.private_key_cert = None
        self.cert = None
        self.cert_ca = None       

        self.private_key = parameters.generate_private_key()
        self.public_key = self.private_key.public_key()

        # Chave partilhada que começa empty
        self.public_key_client = None
        self.shared = None

    
        self.private_key_cert, self.cert, self.cert_ca = validator.get_userdata("MSG_SERVER.p12")
        
    def process(self, msg):
        """ Processa uma mensagem (`bytestring`) enviada pelo CLIENTE.
            Retorna a mensagem a transmitir como resposta (`None` para
            finalizar ligação) """
        self.msg_cnt += 1
        new_msg = b'' # mensagem a enviar como resposta
        global queues

        # Se ainda não houver acordo de chaves
        if self.public_key_client == None:
            # bytes das duas chaves publicas
            self.public_key_client = serialization.load_pem_public_key(msg) #Recebe e processa a chave pública do cliente
            public_key_client_bytes = self.public_key_client.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
            
            public_key_server_bytes = self.public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo) 

            msg = mkpair(public_key_server_bytes, public_key_client_bytes)

            # gera assinatura
            signature = self.private_key_cert.sign(
                msg,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            # envia a mensagem
            cert= self.cert.public_bytes(Encoding.PEM)
            send = mkpair(mkpair(public_key_server_bytes, signature), cert)
            self.msg_cnt -= 1

            # para o programa não ir a baixo
            new_msg = b'Hello World'

        elif self.shared == None:
            signature, client_cert = unpair(msg)

            # Validar certificado do cliente
            cert_Client = x509.load_pem_x509_certificate(client_cert)
            cert_CA = validator.cert_load("MSG_CA.crt")
            

            if validator.valida_certCLIENT(cert_CA, cert_Client):
                print("Client certificate is valid")
            else:
                print("Client certificate is not valid")
                return None
            
            # Verificar assinatura
            try:
                public_key_cert = cert_Client.public_key()
                public_key_cert.verify(
                    signature,
                    mkpair(self.public_key_client.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo), self.public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            except:
                print("Signature is not valid")
                return None
            print("Signature is valid")
            # Shared key
            shared_key = self.private_key.exchange(self.public_key_client)

            # Derivação do segredo partilhado
            self.shared = HKDF(algorithm=hashes.SHA256(),
                               length=32,
                               salt=None,
                               info=b'handshake data').derive(shared_key)
            
            # Obter uid do cliente
            self.uid = validator.get_pseudonym(cert_Client)
            #Adicionar à lista de queues
            if self.uid not in queues:
                queues[self.uid] = []

        else:

            # Cria o algoritmo da cifra
            algorithm = AESGCM(self.shared)

            decrypted = algorithm.decrypt(msg[0:12], msg[12:len(msg)], None) #msg desencriptada
            command_encrypted, msg = unpair(decrypted) 
            command = command_encrypted.decode()

            if command == 'send':
                new_msg = self.send_message(msg)
            elif command == 'askqueue':
                new_msg = self.ask_queue()
            elif command == 'getmsg':
                new_msg = self.get_message(msg)

            print('%r : %r' % (self.uid, command))
            
            # Novo NONCE
            nonce = os.urandom(12)

            # Encriptação e envio da mensagem
            encrypted = algorithm.encrypt(nonce, new_msg, None)
            send = nonce + encrypted

        return send if len(new_msg)>0 else None



    def send_message(self, msg):
        global queues
        msg = utils.parse_message(msg)
        uid = msg.dest_uid
        print("uid: ",uid)
        if uid not in queues:
            msg = "User not found. Message not sent."
        else:
            queues[uid].append((msg, False)) # Adiciona a mensagem à queue
            msg = "Message sent."

        command = "send"
        final_msg = mkpair(command.encode(), msg.encode())
        return final_msg
    

    def ask_queue(self):
        global queues
        if self.uid not in queues:
            msg = "No messages found."
            return mkpair("askqueue".encode(), msg.encode())
        else:
            return utils.ask_queue(queues[self.uid])
    

    def get_message(self, msg):
        global queues
        if queues[self.uid] == []:
            msg = "MSG RELAY SERVICE: unknown message."
            return mkpair("error".encode(), msg.encode())
        num = int.from_bytes(msg, "little")
        msg = utils.get_message(queues[self.uid], num)
        return msg

#
#
# Funcionalidade Cliente/Servidor
#
# obs: não deverá ser necessário alterar o que se segue
#


async def handle_echo(reader, writer):
    global conn_cnt
    conn_cnt +=1
    addr = writer.get_extra_info('peername')
    srvwrk = ServerWorker(conn_cnt, addr)
    # recebe chave publica do cliente
    data = await reader.read(max_msg_size)
    # envia chave publica do servidor, assinatura e certificado
    data = srvwrk.process(data)
    writer.write(data)
    await writer.drain()
    # recebe assinatura e certificado do cliente
    data = await reader.read(max_msg_size)
    data = srvwrk.process(data)

    # espera por novas mesnagens
    data = await reader.read(max_msg_size)
    while True:
        if not data: continue
        if data[:1]==b'\n': break
        data = srvwrk.process(data)
        if data == None:
            break
        if data == False:
            continue
        writer.write(data)
        await writer.drain()
        data = await reader.read(max_msg_size)
    print("[%d]" % srvwrk.id)
    writer.close()


def run_server():
    loop = asyncio.new_event_loop()
    coro = asyncio.start_server(handle_echo, '127.0.0.1', conn_port)
    server = loop.run_until_complete(coro)
    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    print('  (type ^C to finish)\n')
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
    print('\nFINISHED!')

run_server()

