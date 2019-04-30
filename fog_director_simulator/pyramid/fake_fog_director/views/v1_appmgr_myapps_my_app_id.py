from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config


@view_config(route_name='api.v1.appmgr.myapps.my_app_id', request_method='DELETE')
def delete_v1_appmgr_myapps_my_app_id(request: Request) -> Dict[str, Any]:
    raise NotImplementedError()
