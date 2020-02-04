from datetime import datetime


def initialize(sentence):
    now = datetime.now().strftime("%I:%M")
    h, m = now.split(':')
    time = ''
    if int(m) >= 40:
        time = f'It\'s {60 - int(m)} to {int(h)}.'
    else:
        time = f'It\'s {int(m)} past {int(h)}.'

    return [time, f'It\'s {now}']
