import os
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

#cifrar e decifrar ficheiros de texto com a cifra por blocos AES, no modo CTR (Counter)
# a chave e o iv sao lidos de ficheiros binarios em runtime

def encode(args):
    key = open(args[3], "rb").read()
    nonce = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
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
        ciphertext = f.read()

    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    with open(args[2].replace(".enc", ".dec"), "wb") as f:
        f.write(decrypted_data)

def main(argv):
    operations = {
        "enc": encode,
        "dec": decode
    }
    operations[argv[1]](argv)

#test with: python cfich_aes_ctr.py enc file.txt key.key
#test with: python cfich_aes_ctr.py dec file.txt.enc key.key


if __name__ == "__main__":
    main(sys.argv)
