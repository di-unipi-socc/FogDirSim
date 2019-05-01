from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config


@view_config(route_name='api.simulator_frontend.iteration_count.v1', request_method='GET')
def get_simulator_frontend_iteration_count_v1(request: Request) -> Dict[str, Any]:
    raise NotImplementedError()
