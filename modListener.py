import pyaudio
import math
import struct
import time
from deepspeech import Model
import numpy as np

# PyAudio variables
# Threshold = 150
Threshold = 270
SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
swidth = 2
TIMEOUT_LENGTH = 2

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
        print("Finished recording")

        stream_context = self.ds.createStream()
        for frame in rec:
                self.ds.feedAudioContent(
                    stream_context, np.frombuffer(frame, np.int16))
        self.recognizedText = self.ds.finishStream(stream_context)
        print("Recognized: %s" % self.recognizedText)

    def listen(self):
        print('Listening beginning')
        keepLooping = True
        while self.stopVariable is not True:
            input = self.stream.read(chunk)
            rms_val = self.rms(input)
            if rms_val > Threshold:
                self.record()
                return self.recognizedText

    def stop(self):
        self.stopVariable = True