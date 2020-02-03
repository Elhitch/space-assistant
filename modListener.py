import pyaudio
import math
import struct
import wave
import time
import sys
import os
from deepspeech import Model
import numpy as np
#import scipy.io.wavfile as wav

# Global path variables
PATH_TO_DIR = os.path.dirname(os.path.realpath(__file__))
PATH_TO_MODEL = os.path.abspath(os.path.join(PATH_TO_DIR, '../ds-model/'))
#PATH_TO_AUDIO = os.path.abspath(os.path.join(PATH_TO_DIR, 'temp/lastCmd.wav'))

# PyAudio variables
Threshold = 150
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

    def __init__(self, dsModel):
        self.ds = dsModel
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  input_device_index=None,
                                  frames_per_buffer=chunk)
        self.stopVariable = False
        self.recognizedText = None

    def record(self):
        print('Noise detected, recording beginning')
        rec = []
        current = time.time()
        end = time.time() + TIMEOUT_LENGTH

        while current <= end:
            data = self.stream.read(chunk)
            if self.rms(data) >= Threshold:
                end = time.time() + TIMEOUT_LENGTH

            current = time.time()
            rec.append(data)
        # print(data)
        print("Finished recording")
        # self.write(b''.join(rec))

        stream_context = self.ds.createStream()
        for frame in rec:
            if frame is not None:
                self.ds.feedAudioContent(
                    stream_context, np.frombuffer(frame, np.int16))
        self.recognizedText = self.ds.finishStream(stream_context)
        print("Recognized: %s" % self.recognizedText)

    # The following function is not used in the latest versions of the program:
    def write(self, recording):
        filename = os.path.join(PATH_TO_TEMP, 'lastCmd.wav')

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()

    def listen(self):
        print('Listening beginning')
        keepLooping = True
        while True:
            if self.stopVariable is True:
                break
            input = self.stream.read(chunk)
            # print(input)
            rms_val = self.rms(input)
            # print(rms_val)
            if rms_val > Threshold:
                self.record()
                return self.recognizedText

    def stop(self):
        self.stopVariable = True
