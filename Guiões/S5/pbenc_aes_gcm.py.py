import os
import sys
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def derive_key(password,salt,length=16, iterations=100000):
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
    iv = os.urandom(16)
    cipher = AESGCM(key)
    with open(args[2], "rb") as f:
        data = f.read()
    ct = cipher.encrypt(iv, data, None)
    hmac_key = hmac.HMAC(key[32:], hashes.SHA256())
    hmac_key.update(ct)
    signature = hmac_key.finalize()
    with open(args[2] + ".enc", "wb") as f:
        f.write(signature)
        f.write(salt)
        f.write(iv)
        f.write(ct)

def decrypt(args):
    password = input("Enter passphrase: ").encode()
    with open(args[2], "rb") as f:
        signature = f.read(32)
        salt = f.read(16)
        iv = f.read(16)
        ct = f.read()

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