import os
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

#attack based on a word we know is in the plaintext
def chacha20_int_attck(fctxt, pos, ptxtAtPos, newPtxtAtPos):
    with open(fctxt, "rb") as f:
        file_encoded = bytearray(f.read())
    nonce = file_encoded[:16] 
    msg = file_encoded[16:]

    for i in range(pos, pos + len(ptxtAtPos)):  
        msg[i] ^= ord(ptxtAtPos[i - pos]) ^ ord(newPtxtAtPos[i - pos])

    with open(fctxt + '.attck', "wb") as f_attck:
        f_attck.write(nonce + msg)

def main(argv):
    if len(argv) != 5:
        print("Usage: python3 chacha20_int_attck.py <fctxt> <pos> <ptxtAtPos> <newPtxtAtPos>")
        return

    fctxt = argv[1] 
    pos = int(argv[2])
    ptxtAtPos = argv[3]
    newPtxtAtPos = argv[4]

    chacha20_int_attck(fctxt, pos, ptxtAtPos, newPtxtAtPos)

if __name__ == "__main__":
    main(sys.argv)
