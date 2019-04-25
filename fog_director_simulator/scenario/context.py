import os
import sys
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from time import sleep
from typing import Generator
from typing import Optional

from bravado.client import SwaggerClient
from bravado.exception import BravadoConnectionError
from bravado.requests_client import RequestsClient
from bravado_asyncio.http_client import AsyncioClient
from docker import DockerClient
from ephemeral_port_reserve import LOCALHOST
from ephemeral_port_reserve import reserve
from yaml import safe_load

from fog_director_simulator.context_utils import background_process
from fog_director_simulator.context_utils import noop_context


@lru_cache(maxsize=1)
def _api_client(swagger_spec_url):
    with (Path('api_docs') / 'simulator_api' / 'swagger.yaml').open() as f:
        return SwaggerClient.from_spec(
            spec_dict=safe_load(f),
            origin_url=swagger_spec_url,
            http_client=AsyncioClient(),
        )


@lru_cache(maxsize=1)
def _fog_director_client(fog_director_api: str):  # TODO: provide better info on how to use it
    with (Path('api_docs') / 'fog_director_api' / 'swagger.yaml').open() as f:
        client = SwaggerClient.from_spec(
            spec_dict=safe_load(f),
            origin_url=fog_director_api,
            http_client=AsyncioClient(),
        )

        return client


def wait_until_is_up(status_url: str) -> None:
    try:
        RequestsClient().request(request_params={
            'method': 'GET', 'url': status_url,
        }).result()
    except BravadoConnectionError:
        sleep(0.1)  # Sleep a bit ot avoid busy waiting
        wait_until_is_up(status_url)


@contextmanager
def api_context(fog_director_api: Optional[str]) -> Generator[Optional[SwaggerClient], None, None]:
    if fog_director_api is not None:
        with noop_context():
            yield None
        return

    port = reserve()
    url = f'http://{LOCALHOST}:{port}/api'

    with background_process([
        'uwsgi',
        '--http', f':{port}',
        '--wsgi-file', os.path.abspath('simulator_api.wsgi'),
        '--master',
        '--processes', '4',
    ]):
        wait_until_is_up(f'{url}/status')
        print(f'Simulator APIs are up and running on {url}')
        yield _api_client(f'http://{LOCALHOST}:{port}/api/swagger.yaml')


@contextmanager
def fog_director_context(fog_director_api: Optional[str]) -> Generator[SwaggerClient, None, None]:
    if fog_director_api is not None:
        with noop_context():
            yield _fog_director_client(fog_director_api)
        return

    port = reserve()
    url = f'http://{LOCALHOST}:{port}/api'

    with background_process([
        'uwsgi',
        '--http', f':{port}',
        '--wsgi-file', os.path.abspath('fake_fog_director.wsgi'),
        '--master',
        '--processes', '4',
    ]):
        wait_until_is_up(f'{url}/status')
        print(f'Fake Fog Director APIs are up and running on {url}')
        yield _fog_director_client(f'http://{LOCALHOST}:{port}/api/swagger.yaml')


@contextmanager
def simulator_context() -> Generator[None, None, None]:
    # TODO: implement process management

    with run_docker_container(
        image_name='mysql:8.0.15',
        environment={
            'MYSQL_ROOT_PASSWORD': 'password',
        },
        ports={
            '3306/tcp': None,
        },
    ) as container:
        with background_process(args=[
            sys.executable,
            '-m',
            'fog_director_simulator.simulator.engine',
            # TODO: add params
        ]):
            yield container


@contextmanager
def run_docker_container(image_name, command=None, ports=None, environment=None):
    client = DockerClient.from_env()
    container = client.containers.run(
        image=image_name,
        command=command,
        remove=True,
        detach=True,
        ports=ports,
        environment=environment,
    )
    try:
        yield container
    finally:
        container.stop()
