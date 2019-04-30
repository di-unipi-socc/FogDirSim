from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config


@view_config(route_name='api.v1.appmgr.localapps', request_method='GET')
def get_v1_appmgr_localapps(request: Request) -> Dict[str, Any]:
    raise NotImplementedError()
