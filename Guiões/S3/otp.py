import sys
import os

#   A cifra **One-Time-Pad** (OTP) pode ser identificada com a cifra de Vigenère quando a 
#chave é perfeitamente aleatória e com tamanho não inferior ao texto-limpo. No entanto, é 
#normalmente apresentada no alfabeto binário, em que chave e texto-limpor são sequência de bits,
#e a operação para cifrar/decifrar é o **XOR** (ou exclusivo).

##  Fica dificil usar otp na vida real porque a chave tem de ser tao grande quanto a mensagem
## Alem disso, a chave tem de ser completamente aleatoria e nao pode ser reutilizada pois se for reutilizada 
#a seguranca da mensagem e comprometida. 
## Ainda tem os problemas de distribuir a chave e de a guardar em seguranca.

#setup
#Gera um ficheiro com n bytes aleatorios
def setup(nbytes, cipher):
    with open(cipher, "wb") as f: 
        f.write(os.urandom(int(nbytes)))

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