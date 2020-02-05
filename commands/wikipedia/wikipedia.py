import wikipedia


def initialize(sentence):
    sentence = ' '.join(word[0] for word in sentence)
    sentence = sentence.replace('wikipedia', '')
    if not sentence:
        return 'You didn\'t mention what you\'d like on Wikipedia.'
    try:
        results = wikipedia.summary(sentence, sentences=2)
    except:
        return 'Could not find results.'
    return f'According to Wikipedia: {results}'
