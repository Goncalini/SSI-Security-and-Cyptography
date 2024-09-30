import sys

def preproc(str): #
    l=[]
    for c in str:
        if c.isalpha():
            l.append(c.upper())
    return "".join(l)

#Attack to a vigenere cipher
def attackVigenere(file):
    with open(file, "r") as f:
        text = f.read()
    text = preproc(text)
    key = ""
    for i in range(3, 10):
        freq = [0]*26
        for j in range(0, len(text), i):
            freq[ord(text[j])-65] += 1
        key += chr(freq.index(max(freq)) + 65)
    return key


def main(argv):
    if len(argv) != 2:
        return

if __name__ == "__main__":
    main(sys.argv)