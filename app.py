from commands import *


def find_verb(command: str) -> list:
    command = command.strip()
    return command.split(' ')


def main():
    while True:
        command = input('> ')
        print((command))


if __name__ == "__main__":
    main()
