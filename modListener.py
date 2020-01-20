import pyaudio
import math
import struct
import wave
import time
import sys
import os
import pika
""" This script detects sound above certain threshold, records it and writes it to a file. """


# PyAudio variables
Threshold = 270
SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
swidth = 2
TIMEOUT_LENGTH = 2

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
        filename = os.path.join(f_name_directory, 'lastCmd.wav')

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
        sys.exit()
        # message = "modListener: Returning to listening"
        # self.msgBusChannel.basic_publish(exchange='', routing_key=MSG_BUS_CHANNEL, body=message)

    def listen(self):
        print('Listening beginning')
        while True:
            input = self.stream.read(chunk)
            rms_val = self.rms(input)
            if rms_val > Threshold:
                self.record()

recorder = Recorder()
recorder.listen()