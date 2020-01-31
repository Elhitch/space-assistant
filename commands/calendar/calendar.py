from shutil import which
import subprocess
import multiprocessing
import os

functionKeywords = {
    'open': ['open', 'show'],
    'close': ['close', 'hide']
}

def initialize(sentance):
    is_open = False
    calendarProgram = None
    supportedPrograms = ['kontact', 'korganizer', 'gnome-calendar']

    for i in range(len(supportedPrograms)):
        calendarProgram = which(supportedPrograms[i])
        if calendarProgram is not None:
            break

    if not calendarProgram:
        return ('You don\'t have a calendar program installed on your PC.')

    openCalendar(calendarProgram)
    """ Determine the function that needs to be executed: """
    # print(verb)
    # # return openCalendar(calendarProgram)
    # action = None
    # if verb:
    #     for key, value in functionKeywords.items():
    #         if verb[0] in value:
    #             action = key

    #     if action:
    #         if action == 'open':
    #             return openCalendar(calendarProgram)
    #         if action == 'close':
    #             return closeCalendar(calendarProgram)
    # # print(action)
    # else:
    #     if is_open:
    #         is_open = False
    #         return closeCalendar(calendarProgram)
    #     else:
    #         is_open = True
    #         return openCalendar(calendarProgram)

def openCalendar(calendarProgram):
    subprocess.Popen(calendarProgram)
    # multiprocessing.Process(target=calendarProgram)

# def closeCalendar(calendarProgram):
#     program_name = calendarProgram.split('/')[-1]
#     subprocess.call([f'pkill {program_name}'])
