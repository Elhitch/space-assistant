#!/usr/bin/python
import sys
import nltk
import json
import importlib
import speech_recognition as sr
import modSpeech
import os
import subprocess
from deepspeech import Model
import wave
import struct
import time
import math
import pyaudio
import scipy.io.wavfile as wav

from modListener import Recorder

from assistant import Assistant

# Global path variables
PATH_TO_DIR = os.path.dirname(os.path.realpath(__file__))
PATH_TO_MODEL = os.path.abspath(os.path.join(PATH_TO_DIR, '../ds-model/'))
PATH_TO_AUDIO = os.path.abspath(os.path.join(PATH_TO_DIR, 'temp/lastCmd.wav'))

DS_BEAM_WIDTH = 500
DS_LM_WEIGHT = 1.75
DS_WORD_COUNT_WEIGHT = 1.00
DS_VALID_WORD_COUNT_WEIGHT = 1.00


def tagAndTokenize(command: str):
    command = command.strip()
    tokenized = nltk.word_tokenize(command)
    tagged_sentence = nltk.pos_tag(tokenized)
    return tagged_sentence


def find_nouns(tagged_sentence) -> list:
    """Get the verb out of the sentence."""
    """command = command.strip()
    tokenized = nltk.word_tokenize(command)
    
    #global tagged_sentence 
    tagged_sentence = nltk.pos_tag(tokenized)"""
    def is_noun(pos): return pos[:2] == 'NN'
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


if __name__ == "__main__":
    assist = Assistant()
    assist.start()
    # modMsgBusPath = os.path.abspath(os.path.join(PATH_TO_DIR, 'modMsgBus.py'))
    # subprocess.Popen([modMsgBusPath])

    # dsModelPath = os.path.abspath(
    #     os.path.join(PATH_TO_MODEL, "output_graph.pbmm"))
    # dsLMPath = os.path.abspath(os.path.join(PATH_TO_MODEL, "lm.binary"))
    # dsTriePath = os.path.abspath(os.path.join(PATH_TO_MODEL, "trie"))
    # ds = Model(dsModelPath, DS_BEAM_WIDTH)
    # ds.enableDecoderWithLM(dsLMPath, dsTriePath, 0.75, 1.75)

    # inputFromAudio = False
    # for i in range(1, len(sys.argv)):
    #     if sys.argv[i] == "-a":
    #         inputFromAudio = True

    # while True:
    #     r = sr.Recognizer()
    #     with sr.Microphone() as source:
    #         print("Listening...")
    #         audio = r.listen(source)
    #         text = None
    #         try:
    #             text = r.recognize_google(audio)
    #             print(f'You said "{text}"')
    #         except:
    #             print("Couldn't recognize voice")
    #     if text:
    #         sentenceComposition = tagAndTokenize(text)
    #         nouns = find_nouns(sentenceComposition)
    #         module_name = find_module(nouns[::-1])
    #         if not module_name:
    #             print('Couldn\'t find module')
    #         else:
    #             print(f'Module name fould: {module_name}')

    # while True:
    #     if inputFromAudio:
    #         modListener = Recorder()
    #         modListener.listen()
    #         fs, audio = wav.read(PATH_TO_AUDIO)
    #         print("Trying to analyze...")
    #         command = ds.stt(audio)
    #         print("Recognized: " + command)
    #     else:
    #         command = input('> ')

    #     sentenceComposition = tagAndTokenize(command)
    #     nouns = find_nouns(sentenceComposition)
    #     """
    #         Pass a reversed list of nouns. In imperative sentences nouns usually are last so this should speed up the process in find_module(),
    #         especially if the the verb also exists as a noun, e.g. "show".
    #     """
    #     #tagged_sentence = None
    #     module_name = find_module(nouns[::-1])
    #     """
    #         If the command is recognised, perform further analysis to execute the specific action.
    #         Else, notify the user.
    #     """
    #     if module_name != None:
    #         module = importlib.import_module(f'commands.{module_name}')
    #         modInitResult = module.initialize(sentenceComposition)
    #         speechFeedbackEngine = modSpeech.initSpeechFeedback()
    #         modSpeech.say(speechFeedbackEngine, modInitResult)
    #     else:
    #         print("Sorry, I can't understand you.")
