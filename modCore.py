import nltk
import json

class Core:
    def tagAndTokenize(self, command: str):
        command = command.strip()
        tokenized = nltk.word_tokenize(command)
        tagged_sentence = nltk.pos_tag(tokenized)
        return tagged_sentence

    def find_nouns(self, tagged_sentence) -> list:
        """Get the verb out of the sentence."""
        """command = command.strip()
        tokenized = nltk.word_tokenize(command)
        
        #global tagged_sentence 
        tagged_sentence = nltk.pos_tag(tokenized)"""
        is_noun = lambda pos: pos[:2] == 'NN'
        nouns = [word for (word, pos) in tagged_sentence if is_noun(pos)]
        return nouns

    def find_module(self, nouns: str) -> str:
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