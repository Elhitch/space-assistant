from datetime import datetime


def initialize(sentence):
    now = datetime.now().strftime("%I:%M")
    h, m = now.split(':')
    time = ''
    if int(m) >= 40:
        time = f'It\'s {m} to {int(h)}.'
    else:
        time = f'It\'s {m} past {int(h)}.'
    return time
