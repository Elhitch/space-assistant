#!/usr/bin/python
import nltk
import json
import importlib

def find_nouns(command: str) -> list:
    """Get the verb out of the sentence."""
    command = command.strip()
    tokenized = nltk.word_tokenize(command)
    is_noun = lambda pos: pos[:2] == 'NN'
    #global tagged_sentence 
    tagged_sentence = nltk.pos_tag(tokenized)
    nouns = [word for (word, pos) in tagged_sentence if is_noun(pos)]
    return nouns

def find_module(nouns: str) -> str:
    """Find the matching module based on noun"""
    with open('config.json') as f:
        data = json.load(f)
        # print(data['commands'])
        """ Iterate through each item noun in the sentence provided by the user. Necessary to eliminate false-positives nouns, e.g. "show". """
        for noun in nouns:
            for key, values in data['commands'].items():
                if noun in values:
                    return key
        return None

def main():
    while True:
        command = input('> ')

        nouns = find_nouns(command)
        """ 
            Pass a reversed list of nouns. In imperative sentences nouns usually are last so this should speed up the process in find_module(),
            especially if the the verb also exists as a noun, e.g. "show".
        """
        #tagged_sentence = None
        module_name = find_module(nouns[::-1])
        """
            If the command is recognised, perform further analysis to execute the specific action.
            Else, notify the user.
        """
        if module_name != None:
            module = importlib.import_module(f'commands.{module_name}')
            module.initialize()
        else:
            print ("Sorry, I can't understand you.")


if __name__ == "__main__":
    main()
