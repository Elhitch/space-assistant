import nltk
import json
import importlib


def find_nouns(command: str) -> list:
    """Get the verb out of the sentence."""
    command = command.strip()
    tokenized = nltk.word_tokenize(command)
    is_noun = lambda pos: pos[:2] == 'NN'
    nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)]
    return nouns


def find_module(noun: str) -> str:
    """Find the matching module based on noun"""
    with open('config.json') as f:
        data = json.load(f)
        # print(data['commands'])
        for key, values in data['commands'].items():
            if noun[0] in values:
                return key


def main():
    while True:
        command = input('> ')

        nouns = find_nouns(command)
        module_name = find_module(nouns)
        module = importlib.import_module(f'commands.{module_name}')

        module.initialize()


if __name__ == "__main__":
    main()
