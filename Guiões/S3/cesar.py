import sys

def preproc(str):
    l=[]
    for c in str:
        if c.isalpha():
            l.append(c.upper())
    return "".join(l)

#encode 
def encode(key, text):
    key = ord(key.upper()) - ord('A') 
    text = preproc(text)
    l = []
    for c in text:
        l.append(chr((ord(c)-65+key)%26+65)) 
    return "".join(l)

#decode
def decode(key, text):
    key = ord(key.upper()) - ord('A')
    text = preproc(text)
    l = []
    for c in text:
        l.append(chr((ord(c)-65-key)%26+65))
    return "".join(l)


def main(argv):
    if len(argv) != 4:
        return

    function = argv[1] #enc or dec
    key = argv[2] # char
    text = argv[3]
    if function == "enc":
        print(encode(key, text))
    elif function == "dec":
        print(decode(key, text))

if __name__ == "__main__":
    main(sys.argv)