import subprocess


def say(msg):
    command = f'echo "{msg}" | festival --tts'.strip()
    return subprocess.Popen("exec " + command, stdout=subprocess.PIPE, shell=True).pid
