# import datetime
from datetime import date


def initialize(sentence):
    today = date.today()
    return f'It\'s {today.strftime("%B %d, %Y")}'
