import datetime
import sys
import asyncio

import os
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh, padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import validator, utils, protocol

conn_port = 8443
max_msg_size = 9999

# Parâmetros de geração de chaves Diffie-Hellman
g = 2
p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF


parameters = dh.DHParameterNumbers(p, g).parameters()

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

class Client:
    """ Classe que implementa a funcionalidade de um CLIENTE. """
    def __init__(self, sckt=None, argv=None):
        """ Construtor da classe. """
        self.sckt = sckt
        self.msg_cnt = 0

        self.private_key_cert = None
        self.cert = None
        self.cert_ca = None

        self.private_key = parameters.generate_private_key()
        # Definição da chave partilhada usada (vazia no ínicio)
        self.shared = None

        # Definição da chave pública usada (vazia no ínicio)
        self.public_key = None

        fname = None
        if argv is not None and len(argv) > 1:
            fname = argv[2]
        if fname is None:
            self.private_key_cert, self.cert, self.cert_ca = validator.get_userdata("MSG_CLI1.p12")
        elif os.path.exists(fname):
            print("MSG RELAY SERVICE: loading certificate from file", fname)
            self.private_key_cert, self.cert, self.cert_ca = validator.get_userdata(fname)    
        else:
            print("MSG RELAY SERVICE: invalid certificate file!", file=sys.stderr)
            sys.exit(1)  

    #
    # Processamento de mensagens
    #

    def process(self, msg=b""):
        """ Processa uma mensagem (`bytestring`) enviada pelo SERVIDOR.
            Retorna a mensagem a transmitir como resposta (`None` para
            finalizar ligação) """
        self.msg_cnt +=1

        # Caso a chave pública não exista ou não tenha sido partilhada
        if self.public_key == None:

            # Criação da chave pública
            self.public_key = self.private_key.public_key()

            # Serialização da chave publica
            send = self.public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

            # Retrocesso no counter de mensagens
            self.msg_cnt -= 1

            # para programar não ir a baixo
            new_msg = b'Hello World'

        # Caso ainda não tenha sido definido um acordo de chaves
        elif self.shared == None:

            msg_signature, server_cert = unpair(msg)
            # Validar certificado do servidor
            cert_Server = x509.load_pem_x509_certificate(server_cert)
            
            cert_CA = validator.cert_load("MSG_CA.crt")
            
            if validator.valida_certSERVER(cert_CA, cert_Server):
                print("Server certificate is valid")
            else:
                print("Server certificate is not valid")
                return None
            
            # Verificar assinatura
            public_key_server_bytes, signature = unpair(msg_signature)
            public_key_server = serialization.load_pem_public_key(public_key_server_bytes)
            try:
                public_key_cert = cert_Server.public_key()
                public_key_cert.verify(
                    signature,
                    mkpair(public_key_server_bytes, self.public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)),
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
            # Criação do segredo partilhado
            shared_key = self.private_key.exchange(public_key_server)

            # Derivação do segredo partilhado
            self.shared = HKDF(algorithm=hashes.SHA256(),
                               length=32,
                               salt=None,
                               info=b'handshake data').derive(shared_key)

            msg = mkpair(self.public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo),public_key_server_bytes)

            # criar assinatura
            signature = self.private_key_cert.sign(
                msg,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            cert = self.cert.public_bytes(Encoding.PEM)
            send = mkpair(signature, cert)
            
            # Retrocesso no counter de mensagens
            self.msg_cnt -= 1

           # para programar não ir a baixo
            new_msg = b'Hello World'
        else:

            # Criação do algoritmo de cifra
            self.algorithm = AESGCM(self.shared)

            # Cria a variável que irá armazenar a mensagem decifrida (igual à cifrada por defeito no início)
            decrypted = msg

            # Verifica se é uma resposta do servidor
            if len(msg) > 0:
                # Desencriptação da mensagem obtida do servidor
                decrypted = self.algorithm.decrypt(msg[0:12], msg[12:len(msg)], None)
                command_encrypted, msg = unpair(decrypted) 
                command = command_encrypted.decode()
                # Verificação do comando recebido
                if command == 'send':
                    print(msg.decode())
                elif command == 'askqueue':
                    print(msg.decode())
                elif command == 'getmsg':
                    sender, time, subjcet, msg, cert, signature, dest = utils.get_message_client(msg)
                    timestamp = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
                    #print(f"From: {sender}\nTime: {time}\nSubject: {subjcet}\nMessage: {msg} \nDEST: {dest}")
                    cert = x509.load_pem_x509_certificate(cert)
                    cert_CA = validator.cert_load("MSG_CA.crt")
                    msgaux = mkpair(sender.encode(), mkpair(dest.encode(), mkpair(subjcet.encode(), msg.encode())))
                    if validator.valida_certCLIENT(cert_CA, cert):
                        print("Sender certificate is valid")
                    else:
                        print("Sender certificate is not valid")
                    public_key = cert.public_key()
                    try:
                        public_key.verify(
                            signature,
                            msgaux,
                            padding.PSS(
                                mgf=padding.MGF1(hashes.SHA256()),
                                salt_length=padding.PSS.MAX_LENGTH
                            ),
                            hashes.SHA256()
                        )
                        print("Signature is valid, sender is trustworthy")
                    except:
                        print("MSG RELAY SERVICE: verification error!")
                        return None
                    print(f"From: {sender}\nTime: {timestamp}\nSubject: {subjcet}\nMessage: {msg}")
                elif command == 'error':
                    print(msg.decode())
                else:
                    print("MSG RELAY SERVICE: command error!", file=sys.stderr)
                
                return self.process() 

            while True:
                print('O que pretende fazer? --help')
                input_msg = input().split()

                #ignore empty input
                if len(input_msg) == 0:
                    continue
                if input_msg[0] == 'quit':
                    new_msg = b''
                    break
                if not utils.validate_command2(input_msg):
                    print("MSG RELAY SERVICE: command error!", file=sys.stderr)
                    utils.print_help()
                else: 
                    # Verificação do comando introduzido
                    if input_msg[0] == 'send':
                        new_msg = self.send_message(input_msg[1], input_msg[2])
                    elif input_msg[0] == 'askqueue':
                        new_msg = self.ask_queue()
                    elif input_msg[0] == 'getmsg':
                        new_msg = self.get_message(input_msg[1])
                    elif input_msg[0] == 'help':
                        utils.print_help()
                        continue
                    break
                
            if new_msg == False:
                return self.process()
            nonce = os.urandom(12)
            # Encriptação da mensagem pretendida para envio
            encrypted = self.algorithm.encrypt(nonce, new_msg, None)
            # Criação da mensagem para envio
            send = nonce + encrypted
        return send if len(new_msg)>0 else None

# Send message

    def send_message(self, uid, subject): 
        dest = uid
        subject = subject

        print('Input message to send (empty to finish)')
        new_msg = sys.stdin.buffer.readline().strip().decode()
        if (len(new_msg) > 1000):
            print('The message is too long')
            return False

        pseud = validator.get_pseudonym(self.cert)


        new_msg = protocol.Protocol(pseud, dest, subject, new_msg)
        final_msg = new_msg.send_message(self.cert, self.private_key_cert)
        return final_msg


    def ask_queue(self):
        command = "askqueue"
        return mkpair(command.encode(), b'')


    def get_message(self, num):
        if not num.isdigit():
            print('Invalid message number')
            return False
        command = "getmsg"
        num = int(num)
        return mkpair(command.encode(), num.to_bytes(2, "little"))
        

#
#
# Funcionalidade Cliente/Servidor
#
# obs: não deverá ser necessário alterar o que se segue
#


async def tcp_echo_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', conn_port)
    addr = writer.get_extra_info('peername')
    client = Client(addr, sys.argv)
    
    # primeiras iteracoes
    # envia a chave publica
    msg = client.process()
    writer.write(msg)
    # recebe a chave publica do servidor 
    msg = await reader.read(max_msg_size)
    msg = client.process(msg)
    # envia a chave publica e a assinatura
    writer.write(msg)

    # disponiliza terminal para enviar mensagens
    msg = client.process()
    while msg:
        writer.write(msg)
        msg = await reader.read(max_msg_size) #espera pela instrução no terminal
        if msg :
            msg = client.process(msg)
        else:
            break
    writer.write(b'\n')
    print('Socket closed!')
    writer.close()

def run_client():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tcp_echo_client())

if not utils.validate_command(sys.argv[1:]):
    print("MSG RELAY SERVICE: command error!", file=sys.stderr)
    utils.print_help()
    sys.exit(1)

run_client()