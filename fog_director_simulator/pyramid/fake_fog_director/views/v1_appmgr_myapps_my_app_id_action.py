from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config


@view_config(route_name='api.v1.appmgr.myapps.my_app_id.action', request_method='POST')
def post_v1_appmgr_myapps_my_app_id_action(request: Request) -> Dict[str, Any]:
    raise NotImplementedError()
