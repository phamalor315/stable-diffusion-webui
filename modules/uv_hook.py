import sys
import shlex
import subprocess
from functools import wraps


def patch():
    if hasattr(subprocess, "__original_run"):
        return

    print("using uv")
    try:
        subprocess.run(['uv', '-V'])
    except FileNotFoundError:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'uv'])

    subprocess.__original_run = subprocess.run

    @wraps(subprocess.__original_run)
    def patched_run(*args, **kwargs):
        if args:
            command, *_args = args
        else:
            command, _args = kwargs.pop("args", ""), ()

        if isinstance(command, str):
            command = shlex.split(command)
        else:
            command = [arg.strip() for arg in command]

        assert isinstance(command, list)

        if "pip" not in command:
            return subprocess.__original_run([*command, *_args], **kwargs)

        cmd = command[command.index("pip") + 1 :]

        BAD_FLAGS = ("--prefer-binary",)
        cmd = [arg for arg in cmd if arg not in BAD_FLAGS]

        modified_command = ["uv", "pip", *cmd]

        return subprocess.__original_run([*modified_command, *_args], **kwargs)

    subprocess.run = patched_run
