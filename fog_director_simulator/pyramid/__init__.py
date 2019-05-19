import os
from contextlib import contextmanager
from time import sleep
from typing import Any
from typing import Callable
from typing import Generator
from typing import Optional

import pyramid_swagger
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.request import Request
from pyramid.response import Response
from pyramid.tweens import INGRESS
from pyramid_swagger import PyramidSwaggerRendererFactory
from pyramid_swagger.exceptions import RequestValidationError
from pyramid_swagger.exceptions import ResponseValidationError

from fog_director_simulator import database


SIMULATION_TIME_START_HEADER = 'X-Simulation-Time-Start'
SIMULATION_TIME_END_HEADER = 'X-Simulation-Time-End'
DATABASE_LOGIC_SETTING = 'database_logic'


def slow_down_request(wrapped: Callable[[Any, Request], Response]) -> Callable[[Any, Request], Response]:

    def wrapper(context: Any, request: Request) -> Response:
        initial_simulation_time = request.simulation_time
        response = wrapped(context, request)
        while request.database_logic.get_simulation_time() <= initial_simulation_time:
            sleep(0.1)  # Wait a bit to avoid spamming the database too much
        return response

    return wrapper


def _database_logic(request: Request) -> database.DatabaseLogic:
    return request.registry.settings[DATABASE_LOGIC_SETTING]


def _add_simulation_time_response_header_factory(handler: Any, registry: Any) -> Callable[[Request], Response]:
    def add_simulation_time_response_header(request: Request) -> Response:
        request.response.headers[SIMULATION_TIME_START_HEADER] = str(request.simulation_time)
        response = handler(request)
        response.headers[SIMULATION_TIME_END_HEADER] = str(request.database_logic.get_simulation_time())
        return response

    return add_simulation_time_response_header


def _open_database_session_factory(handler: Any, registry: Any) -> Callable[[Request], Response]:
    def open_database_session(request: Request) -> Response:
        with request.database_logic as session:
            try:
                response = handler(request)
                return response
            finally:
                # Ensure that HTTP errors rollback the sessions
                if response.status_code >= 400:
                    session.rollback()

    return open_database_session


@contextmanager
def pyramid_swagger_validation_context(request: Request, response: Optional[Response] = None) -> Generator[None, None, None]:
    try:
        yield
    except ResponseValidationError as response_validation_error:
        raise HTTPInternalServerError(response_validation_error)
    except RequestValidationError as request_validation_error:
        raise HTTPBadRequest(request_validation_error)


def default_pyramid_configuration(
    root_swagger_spec_path: str,
    base_path_api_docs: str,
    database_verbose: bool,
) -> Configurator:
    """Create the WSGI application, post-fork."""
    config = Configurator()

    schema_directory = os.path.dirname(root_swagger_spec_path)
    schema_file = os.path.basename(root_swagger_spec_path)
    config.add_settings({
        'pyramid_swagger.swagger_versions': ['2.0'],
        'pyramid_swagger.enable_response_validation': True,
        'pyramid_swagger.enable_swagger_spec_validation': True,
        # Disable path validation so that simulator_api can handle 404s
        'pyramid_swagger.enable_path_validation': False,
        'pyramid_swagger.schema_directory': schema_directory,
        'pyramid_swagger.schema_file': schema_file,
        'pyramid_swagger.base_path_api_docs': base_path_api_docs,
        'pyramid_swagger.skip_validation': [
            '/(static)\\b',
            f'{base_path_api_docs}(status)\\b',
            f'{base_path_api_docs}(swagger.json)\\b',
            f'{base_path_api_docs}(swagger.yaml)\\b',
        ],
        'pyramid_swagger.validation_context_path': f'{pyramid_swagger_validation_context.__module__}.{pyramid_swagger_validation_context.__name__}',  # noqa

        # Ensure that swagger.json endpoint retrieves the whole spec
        'pyramid_swagger.dereference_served_schema': True,
        # Remove spec references to speed up (a bit) request and response validation
        'bravado_core.internally_dereference_refs': True,
    })

    config.include(pyramid_swagger)

    # Set the default renderer to our JSON renderer
    config.add_renderer(None, PyramidSwaggerRendererFactory())

    config.registry.settings[DATABASE_LOGIC_SETTING] = database.DatabaseClient(config=database.Config.from_environment()).logic
    config.add_request_method(
        lambda request: _database_logic(request),
        name='database_logic',
        property=True,
        reify=True,
    )
    config.add_request_method(
        lambda request: request.database_logic.get_simulation_time(),
        name='simulation_time',
        property=True,
        reify=True,
    )

    config.add_tween(
        tween_factory='{f.__module__}.{f.__name__}'.format(f=_add_simulation_time_response_header_factory),
        under=INGRESS,
    )
    config.add_tween(
        tween_factory='{f.__module__}.{f.__name__}'.format(f=_open_database_session_factory),
        under=INGRESS,
    )

    return config
