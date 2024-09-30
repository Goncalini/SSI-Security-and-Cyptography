import sys

#def wc that counts lines, words, and characters in a file
def wc(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            # Count lines
            lines = len(content.split('\n'))
            # Count words
            words = len(content.split())
            # Count characters
            characters = len(content)

            return lines, words, characters
    except:
        return "File not found."

def main(argv):
    if len(argv) != 2:
        return

    filename = argv[1]
    print(wc(filename))


if __name__ == "__main__":
    main(sys.argv)
