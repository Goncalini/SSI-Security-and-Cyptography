import os
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

#cifrar e decifrar ficheiros de texto com a cifra por blocos AES, no modo CBC (Cipher Block Chaining)
# a chave e o iv sao lidos de ficheiros binarios em runtime

def encode(args):
    key = open(args[3], "rb").read()
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    with open(args[2], "rb") as f:
        data = f.read()
    padder = padding.PKCS7(128).padder()
    data = padder.update(data) + padder.finalize()
    encript_result = encryptor.update(data) + encryptor.finalize()

    with open(args[2] + ".enc", "wb") as f:
        f.write(iv)
        f.write(encript_result)


def decode(args):
    key = open(args[3], "rb").read()
    with open(args[2], "rb") as f:
        iv = f.read(16)
        ciphertext = f.read()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(decrypted_data) + unpadder.finalize()

    with open(args[2].replace(".enc", ".dec"), "wb") as f:
        f.write(data)

 
def main(argv):
    operations = {
        "enc": encode,
        "dec": decode
    }
    operations[argv[1]](argv)

#test with: python cfich_aes_cbc.py enc file.txt key.key
#test with: python cfich_aes_cbc.py dec file.txt.enc key.key
    
if __name__ == "__main__":
    main(sys.argv)