import subprocess


def say(msg):
    command = f'echo "{msg}" | festival --tts'.strip()
    subprocess.call(command, shell=True)
