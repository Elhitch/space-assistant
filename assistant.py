import speech_recognition as sr
from nltk import word_tokenize, pos_tag
from json import load
import pyttsx3


class Assistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.response = pyttsx3.init()
        self.response.setProperty(
            'voice', self.response.getProperty('voices')[1].id)

    def start(self):
        while True:
            voice_command = self._recognize_speech_from_mic(
                self.recognizer, self.microphone)
            if voice_command['success']:
                sentence = voice_command['transcription']
                sentence = self._tag_and_tokenize(sentence)
                nouns = self._get_nouns(sentence)
                module_name = self._get_module_name(nouns)
                if not module_name:
                    self._say('Couldn\'t find module')
                else:
                    self._say(f'Module name found: {module_name}')
            else:
                self._say('I did not understand you.')

    def _recognize_speech_from_mic(self, recognizer, microphone):
        if not isinstance(recognizer, sr.Recognizer):
            raise TypeError("`recognizer` must be `Recognizer` instance")
        if not isinstance(microphone, sr.Microphone):
            raise TypeError("`microphone` must be `Microphone` instance")

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        try:
            response["transcription"] = recognizer.recognize_google(audio)
        except sr.RequestError:
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            response["success"] = False
            response["error"] = "Unable to recognize speech"

        return response

    def _tag_and_tokenize(self, command):
        command = command.strip()
        tokenized = word_tokenize(command)
        tagged_sentence = pos_tag(tokenized)
        return tagged_sentence

    def _get_nouns(self, tagged_sentence):
        def is_noun(pos): return pos[:2] == 'NN'
        return [word for (word, pos) in tagged_sentence if is_noun(pos)]

    def _get_module_name(self, nouns):
        with open('config.json') as f:
            data = load(f)
            for noun in nouns:
                for key, values in data['commands'].items():
                    if noun in values:
                        return key
            return None

    def _say(self, sentence):
        print(f'SAID: {sentence}')
        self.response.say(sentence)
        self.response.runAndWait()
