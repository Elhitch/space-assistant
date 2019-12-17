#!/usr/bin/python
import sys
import nltk
import json
import importlib
import speech_recognition as sr

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
    inputFromAudio = False
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == "-a":
            inputFromAudio = True

    while True:
        if inputFromAudio:
            saAudioInput = sr.Recognizer()  
            with sr.Microphone() as source:
                print("Please wait. Calibrating microphone...")
                # Profile ambient noise for better accuracy
                saAudioInput.adjust_for_ambient_noise(source, duration=5)
                print("Say something!")
                audio = saAudioInput.listen(source)
            
            # (Try to) recognize speech using Sphinx engine
            try:  
                command = saAudioInput.recognize_sphinx(audio)
                print(command)
            except sr.UnknownValueError:
                print("Sphinx could not understand audio")
            except sr.RequestError as e:
                print("Sphinx error; {0}".format(e))
        else:
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
