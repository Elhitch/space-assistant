from datetime import datetime


def initialize(sentence):
    now = datetime.now().strftime("%I:%M")
    h, m = now.split(':')
    time = ''
    if int(m) == 45:
        time = f'It\'s a quarter to {int(h) + 1}.'
    elif int(m) > 30:
        time = f'It\'s {60 - int(m)} to {int(h) + 1}.'
    elif int(m) == 30:
        time = f'It\'s half past {int(h)}.'
    elif int(m) == 0:
        time = f'It\'s {int(h)} o\'clock.'
    elif int(m) == 15:
        time = f'It\'s a quarter past {int(h)}.'
    elif int(m) < 30:
        time = f'It\'s a {int(m)} past {int(h)}.'

    return [time, f'It\'s {now}.']
