# import datetime
from datetime import date


def initialize(sentence):
    today = date.today()
    return today.strftime("%B %d, %Y")
