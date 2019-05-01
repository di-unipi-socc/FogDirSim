from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.pyramid import slow_down_request


@view_config(route_name='api.status', request_method='GET')
@view_config(route_name='api.status_slow', decorator=(slow_down_request, ), request_method='GET')
def get_status(request: Request) -> Dict[str, Any]:
    return {}
