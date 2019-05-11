import os
import subprocess
import sys
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from time import sleep
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from typing import Tuple

from bravado.client import SwaggerClient
from bravado.exception import BravadoConnectionError
from bravado.requests_client import RequestsClient
from docker import DockerClient
from ephemeral_port_reserve import LOCALHOST
from ephemeral_port_reserve import reserve
from sqlalchemy.exc import OperationalError
from yaml import safe_load

from fog_director_simulator.context_utils import background_process
from fog_director_simulator.context_utils import noop_context
from fog_director_simulator.database import Config
from fog_director_simulator.database import DatabaseClient


@lru_cache(maxsize=1)
def _api_client(swagger_spec_url: str) -> SwaggerClient:
    with (Path('api_docs') / 'simulator_api' / 'swagger.yaml').open() as f:
        return SwaggerClient.from_spec(
            spec_dict=safe_load(f),
            origin_url=swagger_spec_url,
        )


@lru_cache(maxsize=1)
def _fog_director_client(fog_director_api: str) -> SwaggerClient:  # TODO: provide better info on how to use it
    with (Path('api_docs') / 'fog_director_api' / 'swagger.yaml').open() as f:
        return SwaggerClient.from_spec(
            spec_dict=safe_load(f),
            origin_url=fog_director_api,
        )


def _wait_until_is_up(process_handle: subprocess.Popen, status_url: str) -> None:
    try:
        if (process_handle.poll() or 0) != 0:
            raise subprocess.CalledProcessError(
                returncode=process_handle.returncode,
                cmd=process_handle.args,
                output=None,
            )
        RequestsClient().request(request_params={
            'method': 'GET', 'url': status_url,
        }).result()
    except BravadoConnectionError:
        sleep(0.1)  # Sleep a bit ot avoid busy waiting
        _wait_until_is_up(process_handle, status_url)


@contextmanager
def api_context(
    database_config: Optional[Config],
    verbose: bool = False,
) -> Generator[Tuple[Optional[subprocess.Popen], Optional[SwaggerClient]], None, None]:
    if database_config is None:
        with noop_context():
            yield None, None
        return

    port = reserve()
    url = f'http://{LOCALHOST}:{port}'

    with background_process(
        name='api_context',
        args=[
            'uwsgi',
            '--http', f':{port}',
            '--wsgi-file', os.path.join('uwsgi', 'simulator_api.wsgi'),
            '--master',
            '--processes', '8',
        ],
        env=database_config.to_environment_dict(override_verbose=False),
        redirect_all_to_std_err=verbose,
    ) as process:
        _wait_until_is_up(process, f'{url}/status')
        print(f'Simulator APIs are up and running on {url}')
        yield process, _api_client(f'http://{LOCALHOST}:{port}/api/swagger.yaml')


@contextmanager
def fog_director_context(
    database_config: Optional[Config],
    fog_director_api_url: Optional[str],
    verbose: bool = False,
) -> Generator[Tuple[Optional[subprocess.Popen], SwaggerClient], None, None]:
    if fog_director_api_url is not None:
        with noop_context():
            yield None, _fog_director_client(fog_director_api_url)
        return

    assert database_config is not None

    port = reserve()
    url = f'http://{LOCALHOST}:{port}'

    with background_process(
        name='fog_director_context',
        args=[
            'uwsgi',
            '--http', f':{port}',
            '--wsgi-file', os.path.join('uwsgi', 'fake_fog_director.wsgi'),
            '--master',
            '--processes', '8',
        ],
        env=database_config.to_environment_dict(override_verbose=False),
        redirect_all_to_std_err=verbose,
    ) as process:
        _wait_until_is_up(process, f'{url}/status')
        print(f'Fake Fog Director APIs are up and running on {url}')
        yield process, _fog_director_client(f'http://{LOCALHOST}:{port}/api/swagger.yaml')


@contextmanager
def _run_docker_container(
    image_name: str,
    command: Optional[List[str]] = None,
    ports: Optional[Dict[str, Optional[str]]] = None,
    environment: Optional[Dict[str, str]] = None,
) -> Generator[Tuple[str, Dict[str, int]], None, None]:
    client = DockerClient.from_env()
    container = client.containers.run(
        image=image_name,
        command=command,
        remove=True,
        detach=True,
        ports=ports,
        environment=environment,
    )
    container_ip = client.api.inspect_container(container.id)['NetworkSettings']['IPAddress']
    container_ports = {
        port: next(iter(
            int(port_object['HostPort'])
            for port_object in client.api.inspect_container(container.id)['NetworkSettings']['Ports'][port]
        ))
        for port in (ports or [])
    }
    try:
        yield container_ip, container_ports
    finally:
        container.stop()


def _wait_until_database_is_up(database_config: Config) -> None:
    try:
        DatabaseClient(config=database_config)
    except OperationalError:
        sleep(0.1)  # Sleep a bit ot avoid busy waiting
        _wait_until_database_is_up(database_config)


@contextmanager
def database_context(start_database: bool, verbose: bool = False) -> Generator[Optional[Config], None, None]:
    if not start_database:
        with noop_context():
            yield None
        return

    with _run_docker_container(
        image_name='postgres:11.2',
        environment={
            'POSTGRES_USER': 'user',
            'POSTGRES_PASSWORD': 'password',
            'POSTGRES_DB': 'fog_director',
        },
        ports={
            '5432/tcp': None,
        },
    ) as (_, container_ports):
        database_config = Config(
            drivername='postgresql+psycopg2',
            username='user',
            password='password',
            host='0.0.0.0',
            port=container_ports['5432/tcp'],
            verbose=verbose,
        )
        _wait_until_database_is_up(database_config)
        print(f'Database up and running on {LOCALHOST}:{database_config.port}')
        yield database_config


@contextmanager
def simulator_context(
    database_config: Optional[Config],
    max_simulation_iterations: int,
    verbose: bool = False,
) -> Generator[Optional[subprocess.Popen], None, None]:
    if database_config is None:
        with noop_context():
            yield None
        return

    args = [
        sys.executable,
        '-m',
        'fog_director_simulator.simulator.engine',
        '--max-simulation-iterations',
        str(max_simulation_iterations),
    ]
    if verbose:
        args.append('--verbose')
    with background_process(
        name='simulator_context',
        args=args,
        env=database_config.to_environment_dict(override_verbose=False),
        redirect_all_to_std_err=verbose,
    ) as process:
        yield process
