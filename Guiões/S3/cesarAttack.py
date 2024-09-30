import sys

def preproc(str):
    l=[]
    for c in str:
        if c.isalpha():
            l.append(c.upper())
    return "".join(l)

#Attack to a caesar cipher
def attack(file):
    #to attack a caesar cipher we can use the fact that the most common letter in english is 'E'
    #so we can use the frequency of the letters to find the key
    with open(file, "r") as f:
        text = f.read()
    text = preproc(text)
    freq = [0]*26 
    for c in text:
        freq[ord(c)-65] += 1
    key = freq.index(max(freq)) - 4
    return key


def main(argv):
    if len(argv) != 2:
        return
    
    file = argv[1]
    print(attack(file))



if __name__ == "__main__":
    main(sys.argv)