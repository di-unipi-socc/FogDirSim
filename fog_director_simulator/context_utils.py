import signal
import subprocess
from contextlib import contextmanager
from typing import List


@contextmanager
def background_process(args: List[str], stdout: int = subprocess.PIPE, stderr: int = subprocess.PIPE):
    process = subprocess.Popen(args=args, encoding='utf-8', stdout=stdout, stderr=stderr)
    try:
        yield process
    finally:
        process.send_signal(signal.SIGQUIT)
        try:
            process.communicate(timeout=0.1)
        except subprocess.TimeoutExpired:
            process.kill()


@contextmanager
def noop_context():
    yield
