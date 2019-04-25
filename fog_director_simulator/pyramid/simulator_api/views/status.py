from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config


@view_config(route_name='api.status')
def status(request: Request) -> Dict[str, Any]:
    return {}
