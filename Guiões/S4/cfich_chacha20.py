import os, struct, sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

def setup(file):
    name = file[2]
    key = os.urandom(32)
    with open(name, "wb") as f:
        f.write(key)

def encode(args):
    key = open(args[3], "rb").read()
    nonce = os.urandom(16)
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
    encryptor = cipher.encryptor()
    with open(args[2], "rb") as f:
        data = f.read()
    encript_result = encryptor.update(data) + encryptor.finalize()
    with open(args[2] + ".enc", "wb") as f:
        f.write(nonce)
        f.write(encript_result)

def decode(args):
    key = open(args[3], "rb").read()
    with open(args[2], "rb") as f:
        nonce = f.read(16)
        encript_result = f.read()
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
    decryptor = cipher.decryptor()
    pt = decryptor.update(encript_result) + decryptor.finalize()
    with open(args[2] + ".dec", "wb") as f:
        f.write(pt)

def main(argv):
    operations = {
        "setup": setup,
        "enc": encode,
        "dec": decode
    }

    operations[argv[1]](argv)

if __name__ == "__main__":
    main(sys.argv)