from datetime import datetime


def initialize(sentence):
    now = datetime.now()
    return now.strftime("%H:%M")
