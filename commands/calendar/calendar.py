from shutil import which
import subprocess
import multiprocessing

functionKeywords = {
    'open': ['open', 'show'],
    'close': ['close', 'hide']
}

def initialize(sentence):
    is_open = False
    calendarProgram = None
    supportedPrograms = ['kontact', 'korganizer', 'gnome-calendar']

    for i in range(len(supportedPrograms)):
        calendarProgram = which(supportedPrograms[i])
        if calendarProgram is not None:
            break

    if not calendarProgram:
        return ('You don\'t have a calendar program installed on your PC.')

    """
        Call the respective function. Last and default action if no other is seen
        is to open the calendar.
    """
    openCalendar(calendarProgram)
    return "Alright, opening your calendar."
    """ Determine the function that needs to be executed: """

def openCalendar(calendarProgram):
    subprocess.Popen(calendarProgram)