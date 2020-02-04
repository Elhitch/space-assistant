from datetime import datetime


def initialize(sentence):
    now = datetime.now()
    now_feedback = "It is " + now.strftime("%H:%M") + "."
    return now_feedback
