import webbrowser
import wikipedia


def initialize(sentance):
    sentence = sentance.replace('wikipedia', '')
    results = wikipedia.summary(query, sentences=2)
    return f'According to wikipedia {results}'
