import os
import signal
import subprocess
import sys
from contextlib import contextmanager
from itertools import chain
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional


@contextmanager
def background_process(
    args: List[str],
    env: Optional[Dict[str, Any]] = None,
    redirect_all_to_std_err: bool = False,
) -> Generator[subprocess.Popen, None, None]:
    process = subprocess.Popen(
        args=args,
        encoding='utf-8',
        stdout=sys.stderr.buffer if redirect_all_to_std_err else subprocess.PIPE,
        stderr=sys.stderr.buffer if redirect_all_to_std_err else subprocess.PIPE,
        env=dict(
            os.environ,
            PATH=os.pathsep.join(chain(
                os.path.dirname(sys.executable),
                os.environ.get('PATH', '').split(os.pathsep)
            )),
            **(env or {})
        ),
    )
    try:
        yield process
    finally:
        process.send_signal(signal.SIGQUIT)
        try:
            process.communicate(timeout=0.1)
        except subprocess.TimeoutExpired:
            process.kill()


@contextmanager
def noop_context() -> Generator[None, None, None]:
    yield
