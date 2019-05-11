import os
import signal
import subprocess
import sys
from contextlib import contextmanager
from itertools import chain
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional


@contextmanager
def background_process(
    name: str,
    args: List[str],
    env: Optional[Dict[str, Any]] = None,
    redirect_all_to_std_err: bool = False,
) -> Generator[subprocess.Popen, None, None]:
    if not redirect_all_to_std_err:
        directory = Path('.logs') / str(os.getpid()) / name
        print(f'Logs will be written on {directory}', file=sys.stderr)
        directory.mkdir(parents=True, exist_ok=True)
        stdout = (directory / 'stdout').open('w')
        stderr = (directory / 'stderr').open('w')
    else:
        stdout = sys.stderr.buffer
        stderr = sys.stderr.buffer
    process = subprocess.Popen(
        args=args,
        encoding='utf-8',
        stdout=stdout,
        stderr=stderr,
        env=dict(
            os.environ,
            PATH=os.pathsep.join(chain(
                os.path.dirname(sys.executable),
                os.environ.get('PATH', '').split(os.pathsep)
            )),
            **(env or {})
        ),
    )
    print(f'Starting process {args}. pid={process.pid}', file=sys.stderr)
    try:
        yield process
    except BaseException as e:
        print(f'[{name}] Caught exception {e}')
        raise
    finally:
        return_code = process.poll()
        if return_code is None:
            print(f'Background process {args} did not exit yet. Killing it.')
        else:
            print(f'Background process {args} exited with return_code={return_code}.')
        process.send_signal(signal.SIGQUIT)
        try:
            process.communicate(timeout=0.1)
        except subprocess.TimeoutExpired:
            process.kill()


@contextmanager
def noop_context() -> Generator[None, None, None]:
    yield
