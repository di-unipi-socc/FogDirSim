from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config


@view_config(route_name='api.v1.appmgr.localapps.upload', request_method='POST')
def post_v1_appmgr_localapps_upload(request: Request) -> Dict[str, Any]:
    raise NotImplementedError()
