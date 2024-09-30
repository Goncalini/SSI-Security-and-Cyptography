import os
import sys
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_key(password, salt, length=32, iterations=100000):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=iterations
    )
    return kdf.derive(password)

def encrypt(args):
    password = input("Enter passphrase: ").encode()
    salt = os.urandom(16)
    key = derive_key(password, salt)
    iv = os.urandom(12)
    cipher = ChaCha20Poly1305(key)
    with open(args[2], "rb") as f:
        data = f.read()

    ct = cipher.encrypt(iv, data, None)
    with open(args[2] + ".enc", "wb") as f:
        f.write(salt)
        f.write(iv)
        f.write(ct)

def decrypt(args):
    password = input("Enter passphrase: ").encode()
    with open(args[2], "rb") as f:
        salt = f.read(16)
        iv = f.read(12)
        ct = f.read()

    key = derive_key(password, salt)
    cipher = ChaCha20Poly1305(key)
    pt = cipher.decrypt(iv, ct, None)
    with open(args[2] + ".dec", "wb") as f:
        f.write(pt)

def main(args):
    operations = {
        "enc": encrypt,
        "dec": decrypt
    }

    operations[args[1]](args)

if __name__ == "__main__":
    main(sys.argv)  