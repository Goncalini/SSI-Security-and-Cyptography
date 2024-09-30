# Código baseado em https://docs.python.org/3.6/library/asyncio-stream.html#tcp-echo-client-using-streams
import asyncio
import socket
import os
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import dh, padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import validator
from cryptography import x509


conn_port = 8443
max_msg_size = 9999

# Parâmetros para a geração de chaves Diffie-Hellman dado no enunciado
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
    def __init__(self, sckt=None):
        """ Construtor da classe. """
        self.sckt = sckt
        self.msg_cnt = 0

        # Load chave secreta usada pelo cliente
        with open('MSG_CLI1.key', 'rb') as key_file:
            self.private_key_cert = serialization.load_pem_private_key(
                key_file.read(),
                password=b"1234",
            )

        self.private_key = parameters.generate_private_key()
       # Chave partilhada que começa empty
        self.shared = None

        # Chave publica que começa empty
        self.public_key = None

    def process(self, msg=b""):
        """ Processa uma mensagem (`bytestring`) enviada pelo SERVIDOR.
            Retorna a mensagem a transmitir como resposta (`None` para
            finalizar ligação) """
        self.msg_cnt +=1

        # Temos de ter a certeza que geramos uma public key
        if self.public_key == None:
            self.public_key = self.private_key.public_key() #criar chave publica
            send = self.public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
            self.msg_cnt -= 1

            # temos de encher a msg pq pode acabar com o programa 
            new_msg = b'Hello World'

        # Se ainda não houver acordo de chaves
        elif self.shared == None:

            msg_signature, server_cert = unpair(msg)
            # Validar certificado do servidor
            cert = x509.load_pem_x509_certificate(server_cert)
            cert_CA = validator.cert_load("MSG_CA.crt")
            if validator.valida_certSERVER(cert_CA, cert):
                print("Server certificate is valid")
            else:
                print("Server certificate is not valid")
                return None
            
            # Verificar assinatura
            public_key_server_bytes, signature = unpair(msg_signature)
            public_key_server = serialization.load_pem_public_key(public_key_server_bytes) # Recebe a chave pública do servidor
            try:
                public_key_cert = cert.public_key()
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

            # Cria e depois gera a chave partilhada
            shared_key = self.private_key.exchange(public_key_server)
            self.shared = HKDF(algorithm=hashes.SHA256(),
                               length=32,
                               salt=None,
                               info=b'handshake data').derive(shared_key)

            msg = mkpair(self.public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo),public_key_server_bytes)

            # Autentica a signatura
            signature = self.private_key_cert.sign(
                msg,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            # load do certificado
            with open('MSG_CLI1.crt', 'rb') as cert_file:
                cert = cert_file.read()

            send = mkpair(signature, cert)
            
            self.msg_cnt -= 1

            # Mesmo que em cima
            new_msg = b'Hello World'
        else:

            # Cria o algoritmo da cifra
            algorithm = AESGCM(self.shared)

            decrypted = msg #msg desencriptada

            # Verifica se a mensagem não é a de inicialização
            if len(msg) > 0:
                # Desencriptação da mensagem obtida do servidor
                decrypted = algorithm.decrypt(msg[0:12], msg[12:len(msg)], None)
        
            # Impressão da mensagem recebida
            print('Received (%d): %r' % (self.msg_cnt , decrypted.decode()))
            print('Input message to send (empty to finish)')
            new_msg = input().encode()

            # novo nonce
            nonce = os.urandom(12)

            # Encriptação e envio da mensagem
            encrypted = algorithm.encrypt(nonce, new_msg, None)
            send = nonce + encrypted

        return send if len(new_msg)>0 else None

#
#
# Funcionalidade Cliente/Servidor
#
# obs: não deverá ser necessário alterar o que se segue
#


async def tcp_echo_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', conn_port)
    addr = writer.get_extra_info('peername')
    client = Client(addr)
    
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
        msg = await reader.read(max_msg_size)
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


run_client()