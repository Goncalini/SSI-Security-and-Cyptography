import asyncio
from hashlib import pbkdf2_hmac, sha256
import hmac
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes

conn_cnt = 0
conn_port = 8443
max_msg_size = 9999

def derive_key(password, salt, length=16, iterations=100000):
    kdf = pbkdf2_hmac(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt, 
        iterations=iterations
    )
    return kdf.derive(password)

def generate_signature(message, key):
    key = key.encode()
    message = message.encode()
    signature = hmac.new(key, message, sha256).digest()

    return signature

class ServerWorker(object):
    """ Classe que implementa a funcionalidade do SERVIDOR. """
    def __init__(self, cnt, addr=None):
        """ Construtor da classe. """
        self.id = cnt
        self.addr = addr
        self.msg_cnt = 0
    def process(self, msg):
        """ Processa uma mensagem (`bytestring`) enviada pelo CLIENTE.
            Retorna a mensagem a transmitir como resposta (`None` para
            finalizar ligação) """
        self.msg_cnt += 1
        password = generate_signature("password", "salt")
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
        print('%d : %r' % (self.id,pt))
        new_msg = pt.upper()
        password = generate_signature("password", "salt")
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


async def handle_echo(reader, writer):
    global conn_cnt
    conn_cnt +=1
    addr = writer.get_extra_info('peername')
    srvwrk = ServerWorker(conn_cnt, addr)
    data = await reader.read(max_msg_size)
    while True:
        if not data: continue
        if data[:1]==b'\n': break
        data = srvwrk.process(data)
        if not data: break
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