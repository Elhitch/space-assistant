from commands import *
import nltk


def find_verb(command: str) -> list:
    """Get the verb out of the sentence."""
    command = command.strip()
    tokenized = nltk.word_tokenize(command)
    print(nltk.pos_tag(tokenized))
    is_verb = lambda pos: pos[:2] == 'VB'
    verbs = [word for (word, pos) in nltk.pos_tag(tokenized) if is_verb(pos)]
    return verbs


def main():
    while True:
        command = input('> ')
        print(find_verb(command))


if __name__ == "__main__":
    main()
