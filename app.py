#!/usr/bin/python
import sys
import nltk
import json
import importlib
import speech_recognition as sr
import modSpeech
import pika
import os
import subprocess
from deepspeech import Model
import wave
import struct
import time
import math
import pyaudio
import scipy.io.wavfile as wav

# Global path variables
PATH_TO_DIR = os.path.dirname(os.path.realpath(__file__))
PATH_TO_MODEL = os.path.abspath(os.path.join(PATH_TO_DIR, '../ds-model/'))
PATH_TO_AUDIO = os.path.abspath(os.path.join(PATH_TO_DIR, 'temp/lastCmd.wav'))

# PyAudio variables
Threshold = 270
SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
swidth = 2
TIMEOUT_LENGTH = 2
PATH_TO_TEMP = os.path.abspath(os.path.join(PATH_TO_DIR, 'temp/'))

# Name of the channel to emit messages to
MSG_BUS_CHANNEL = "mainComm"

f_name_directory = os.getcwd() + '/temp'
class Recorder:

    @staticmethod
    def rms(frame):
        count = len(frame) / swidth
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  input_device_index=None,
                                  frames_per_buffer=chunk)
        self.msgBusConnection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.msgBusChannel = self.msgBusConnection.channel()
        self.msgBusChannel.queue_declare(queue="mainComm")
        # message = "modListener: Initialized"
        # self.msgBusChannel.basic_publish(exchange='', routing_key="mainComm", body=message)

    def record(self):
        print('Noise detected, recording beginning')
        # message = "modListener: Noise detected, beginning to record sound"
        # self.msgBusChannel.basic_publish(exchange='', routing_key=MSG_BUS_CHANNEL, body=message)
        rec = []
        current = time.time()
        end = time.time() + TIMEOUT_LENGTH

        while current <= end:
            data = self.stream.read(chunk)
            if self.rms(data) >= Threshold: end = time.time() + TIMEOUT_LENGTH

            current = time.time()
            rec.append(data)
        print("Finished recording")
        # message = "modListener: Finished recording sound"
        # self.msgBusChannel.basic_publish(exchange='', routing_key=MSG_BUS_CHANNEL, body=message)
        self.write(b''.join(rec))

    def write(self, recording):
        filename = os.path.join(PATH_TO_TEMP, 'lastCmd.wav')

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()
        #print('Written to file: {}'.format(filename))
        message = "modListener: Written recording to file {}".format(filename)
        self.msgBusChannel.basic_publish(exchange='', routing_key=MSG_BUS_CHANNEL, body=message)
        #print('Returning to listening')
        #sys.exit()
        # message = "modListener: Returning to listening"
        # self.msgBusChannel.basic_publish(exchange='', routing_key=MSG_BUS_CHANNEL, body=message)

    def listen(self):
        print('Listening beginning')
        keepLooping = True
        while keepLooping:
            input = self.stream.read(chunk)
            rms_val = self.rms(input)
            if rms_val > Threshold:
                self.record()
                keepLooping = False

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
    is_noun = lambda pos: pos[:2] == 'NN'
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
    modMsgBusPath = os.path.abspath(os.path.join(PATH_TO_DIR, 'modMsgBus.py'))
    subprocess.Popen([modMsgBusPath])

    dsModelPath = os.path.abspath(os.path.join(PATH_TO_MODEL, "output_graph.pbmm"))
    dsLMPath = os.path.abspath(os.path.join(PATH_TO_MODEL, "lm.binary"))
    dsTriePath = os.path.abspath(os.path.join(PATH_TO_MODEL, "trie"))
    ds = Model(dsModelPath, DS_BEAM_WIDTH)
    ds.enableDecoderWithLM(dsLMPath, dsTriePath, 0.75, 1.75)
    
    inputFromAudio = False
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == "-a":
            inputFromAudio = True

    while True:
        if inputFromAudio:
            modListener = Recorder()
            modListener.listen()
            print("Recorded audio")
            fs, audio = wav.read(PATH_TO_AUDIO)
            print("Trying to analyze...")
            command = ds.stt(audio)
            print("Recognized: " + command)
        else:
            command = input('> ')

        sentenceComposition = tagAndTokenize(command)
        nouns = find_nouns(sentenceComposition)
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
            modInitResult = module.initialize(sentenceComposition)
            speechFeedbackEngine = modSpeech.initSpeechFeedback()
            modSpeech.say(speechFeedbackEngine, modInitResult)
        else:
            print ("Sorry, I can't understand you.")