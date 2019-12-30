import pyttsx3

def initSpeechFeedback():
    # Currently using espeak, look into possibilities to replace it with Festival
    speechFeedbackEngine = pyttsx3.init()
    #rate = speechFeedbackEngine.getProperty('rate')
    speechFeedbackEngine.setProperty('rate', 150)
    speechFeedbackEngine.setProperty('voice', 'english+f1')
    return speechFeedbackEngine

def say(speechFeedbackEngine, msg):
    print (msg)
    speechFeedbackEngine.say(msg)
    speechFeedbackEngine.runAndWait()