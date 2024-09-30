import os, struct, sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


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
    print(len(nonce))
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
    encryptor = cipher.encryptor()
    with open(args[2], "rb") as f:
        data = f.read()
    encript_result = encryptor.update(data) + encryptor.finalize()
    with open(args[2] + ".enc", "wb") as f:
        f.write(salt)
        f.write(nonce)
        f.write(encript_result)


def decode(args):
    password = input("Password: ")
    with open(args[2], "rb") as f:
        salt = f.read(16)
        nonce = f.read(16)
        encript_result = f.read()
    key = derive_kdf(password,salt)
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
    decryptor = cipher.decryptor()
    pt = decryptor.update(encript_result) + decryptor.finalize()
    with open(args[2] + ".dec", "wb") as f:
        f.write(pt)



#deixa de existir a criação de nova chave
def main(argv):
    operations = {
        "enc": encode,
        "dec": decode
    }
    operations[argv[1]](argv)


if __name__ == "__main__":
    main(sys.argv)