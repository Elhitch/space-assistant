import webbrowser
import wikipedia


def initialize(sentence):
    sentence = ' '.join(word[0] for word in sentence)
    sentence = sentence.replace('wikipedia', '')
    results = wikipedia.summary(sentence, sentences=2)
    return f'According to wikipedia {results}'
