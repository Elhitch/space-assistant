import subprocess


def say(msg):
    command = f'echo "{msg}" | festival --tts'.strip()
    subprocess.Popen(command, shell=True)
