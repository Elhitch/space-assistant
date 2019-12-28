from shutil import which

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
    
    #for key, value in functionKeywords.items():


def openCalendar():
    return ("Alright, opening your calendar - " + calendarProgram)
