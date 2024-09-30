import sys
import os
import random


# Implementation of a bad pseudo-random number generator
def bad_prng(n):
    random.seed(random.randbytes(2))
    return random.randbytes(n)

#setup
#Generates a file with n bytes of random data
def setup(nbytes, cipher):
    with open(cipher, "wb") as f: 
        bytes = bad_prng(int(nbytes))
        #bytes = os.urandom(int(nbytes))
        f.write(bytes)

#encode reads the cipher file and xors it with the message file
def encode(file, cipher):
    filename = file
    with open(file, "rb") as f:
        file = f.read()
    with open(cipher, "rb") as f:
        cipher = f.read()
    #cip file .enc
    with open(filename + ".enc", "wb") as f:
        f.write(bytes([a^b for a, b in zip(file, cipher)]))


#decode reads the cipher file and xors it with the message file
def decode(file, cipher):
    filename = file
    with open(file, "rb") as f:
        file = f.read()
    with open(cipher, "rb") as f:
        cipher = f.read()
    with open(filename + ".dec", "wb") as f:
        f.write(bytes([a^b for a, b in zip(file, cipher)]))


def main(argv):
    if len(argv) != 4:
        return

    function = argv[1] #setup, enc or dec
    arg1 = argv[2] # nbytes for setup and message file for enc and dec
    arg2 = argv[3] # cipher file for all functions
    if function == "setup":
        setup(arg1, arg2)
    elif function == "enc":
        print(encode(arg1, arg2))
    elif function == "dec":
        print(decode(arg1, arg2))

if __name__ == "__main__":
    main(sys.argv)