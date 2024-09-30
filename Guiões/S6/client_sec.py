import asyncio
import os
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

conn_port = 8443
max_msg_size = 9999

def derive_key(password,salt,length=16, iterations=100000):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=iterations
    )
    return kdf.derive(password)

def generate_signature(message, key):
    key = key.encode()
    message = message.encode()
    signature = hmac.HMAC(key, hashes.SHA256())

    return signature

class Client:
    """ Classe que implementa a funcionalidade de um CLIENTE. """
    def __init__(self, sckt=None):
        """ Construtor da classe. """
        self.sckt = sckt
        self.msg_cnt = 0
    def process(self, msg=b""):
        """ Processa uma mensagem (`bytestring`) enviada pelo SERVIDOR.
            Retorna a mensagem a transmitir como resposta (`None` para
            finalizar ligação) """
        self.msg_cnt +=1
        #password = generate_signature("password", "salt")
        password = b"password"
        signature = msg[:32]
        salt = msg[32:48]
        iv = msg[48:64]
        ct = msg[64:]

        key = derive_key(password, salt)
        hmac_key = hmac.HMAC(key[32:], hashes.SHA256())
        hmac_key.update(ct)
        try:
            hmac_key.verify(signature)
        except:
            print("Invalid signature")
            return
        cipher = AESGCM(key)
        pt = cipher.decrypt(iv, ct, None)
        print('Received (%d): %r' % (self.msg_cnt , pt.decode()))
        print('Input message to send (empty to finish)')
        #password = generate_signature("password", "salt")
        password = b"password"
        salt = os.urandom(16)
        key = derive_key(password, salt)
        iv = os.urandom(16)
        cipher = AESGCM(key)
        new_msg = input().encode()
        ct = cipher.encrypt(iv, new_msg, None)
        hmac_key = hmac.HMAC(key[32:], hashes.SHA256())
        hmac_key.update(ct)
        signature = hmac_key.finalize()
        new_msg = signature + salt + iv + ct
        return new_msg if len(new_msg)>0 else None



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