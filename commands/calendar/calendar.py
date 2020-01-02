from shutil import which
import subprocess

functionKeywords = {
    "open": ["open", "start", "show"]
}

def initialize(command: str):
    supportedPrograms = ["kontact", "korganizer"]
    calendarProgram = None
    i = 0
    while (calendarProgram == None):
        calendarProgram = (which(supportedPrograms[i]))
    if calendarProgram is None:
        return ("You don't have a calendar program installed on your PC.")

    """ Determine the function that needs to be executed: """
    
    return openCalendar(calendarProgram)
    #for key, value in functionKeywords.items():


def openCalendar(calendarProgram):
    subprocess.call([calendarProgram])
    return ("Alright, opening your calendar")
