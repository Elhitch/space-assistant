#!/usr/bin/python
import sys
import nltk
import json
import importlib
import speech_recognition as sr
import modSpeech
import pika
import os

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

def processMessage(ch, method, properties, body):
    message = body.decode("utf-8")
    print(message)

if __name__ == "__main__":
    try:
        os.system("service rabbitmq-server start")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='mainComm')
        channel.basic_consume(queue='mainComm', on_message_callback=processMessage, auto_ack=True)
        channel.start_consuming()
    except Exception as e:
        print("Couldn't start RabbitMQ server, shutting down...")
        print(e)
        sys.exit()

    inputFromAudio = False
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == "-a":
            inputFromAudio = True

    while True:
        if inputFromAudio:
            saAudioInput = sr.Recognizer()  
            with sr.Microphone() as source:
                print("Please wait. Calibrating microphone...")
                """ Profile ambient noise for better accuracy """
                saAudioInput.adjust_for_ambient_noise(source, duration=5)
                print("Say something!")
                audio = saAudioInput.listen(source)
            
            """ (Try to) recognize speech using Sphinx engine """
            try:  
                command = saAudioInput.recognize_sphinx(audio)
                print(command)
            except sr.UnknownValueError:
                print("Sphinx could not understand audio")
            except sr.RequestError as e:
                print("Sphinx error; {0}".format(e))
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