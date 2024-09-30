import sys

def preproc(str):
    l=[]
    for c in str:
        if c.isalpha():
            l.append(c.upper())
    return "".join(l)

#encode
def encode(key, text):
    key = preproc(key)
    text = preproc(text)
    l = []
    for i in range(len(text)):
        k = ord(key[i%len(key)]) - ord('A')
        l.append(chr((ord(text[i])-65+k)%26+65))
    return "".join(l)

#decode
def decode(key, text):
    key = preproc(key)
    text = preproc(text)
    l = []
    for i in range(len(text)):
        k = ord(key[i%len(key)]) - ord('A')
        l.append(chr((ord(text[i])-65-k)%26+65))
    return "".join(l)


def main(argv):
    if len(argv) != 4:
        return

    function = argv[1] #enc or dec
    key = argv[2] #string
    text = argv[3]
    if function == "enc":
        print(encode(key, text))
    elif function == "dec":
        print(decode(key, text))

if __name__ == "__main__":
    main(sys.argv)
