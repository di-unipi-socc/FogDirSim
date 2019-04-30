from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config


@view_config(route_name='api.v1.appmgr.myapps', request_method='POST')
def post_v1_appmgr_myapps(request: Request) -> Dict[str, Any]:
    raise NotImplementedError()


@view_config(route_name='api.v1.appmgr.myapps', request_method='GET')
def get_v1_appmgr_myapps(request: Request) -> Dict[str, Any]:
    raise NotImplementedError()
