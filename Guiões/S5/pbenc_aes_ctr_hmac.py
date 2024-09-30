import os, struct, sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def enc_hmac_SHA256(key,data):
    h = hmac.HMAC(key, hashes.SHA256())
    h.update(data)
    s = h.finalize()
    return s


def dec_hmac_SHA256(key,data,signature):
    h = hmac.HMAC(key, hashes.SHA256())
    h.update(data)
    return h.verify(signature)



def derive_kdf(password, salt):
    kdf = PBKDF2HMAC(
         algorithm=hashes.SHA256(),
         length=32,
         salt=salt,
         iterations=480000,
        )
    return kdf.derive(password.encode('utf-8'))


def encode(args):
    password = input("Password: ")
    salt = os.urandom(16)
    key = derive_kdf(password,salt)

    nonce = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    encryptor = cipher.encryptor()

    with open(args[2], "rb") as f:
        data = f.read()
    encript_result = encryptor.update(data) + encryptor.finalize()
    sig = enc_hmac_SHA256(key,encript_result)

    with open(args[2] + ".enc", "wb") as f:
        f.write(salt)
        f.write(sig)
        f.write(nonce)
        f.write(encript_result)


def decode(args):
    password = input("Password: ")
    with open(args[2], "rb") as f:
        salt = f.read(16)
        signature = f.read(32)
        nonce = f.read(16)
        encript_result = f.read()

    key = derive_kdf(password,salt)

    dec_hmac_SHA256(key, encript_result, signature)

    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    decryptor = cipher.decryptor()
    pt = decryptor.update(encript_result) + decryptor.finalize()
    with open(args[2] + ".dec", "wb") as f:
        f.write(pt)


#encoding: update(ct) e s = finalize
#decode: update(CT) com o conteudo cifrado e verify(S) - é a assinatura q lemos do ficheiro

#deixa de existir a criação de nova chave
def main(argv):
    operations = {
        "enc": encode,
        "dec": decode
    }
    operations[argv[1]](argv)


if __name__ == "__main__":
    main(sys.argv)