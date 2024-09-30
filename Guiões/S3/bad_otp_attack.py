import sys
import random

#Attack bad otp cipher using a list of words that are expected to be in the message
def attack(file, words):
    #open ciphred message file
    with open(file, "rb") as f:
        file = f.read()
    
    #We know that random has 2^16 possible states so we can try all of them
    for i in range(2**16):
        random.seed(i.to_bytes(2, "big"))
        cipher = random.randbytes(len(file))
        message = bytes([a^b for a, b in zip(file, cipher)])
        #check if the message contains all the words
        if all(word in message.decode() for word in words):
            return message
        
    return "Message not found"       
    


def main(argv):
    #receives a file and a list of words
    if len(argv) < 3:
        return
    file = argv[1]
    words = argv[2:]


if __name__ == "__main__":
    main(sys.argv)