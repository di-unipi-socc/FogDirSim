from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config


@view_config(route_name='api.v1.appmgr.tokenservice', request_method='POST')
def post_v1_appmgr_tokenservice(request: Request) -> Dict[str, Any]:
    return {
        'token': 'string',
        'expiryTime': 0,
        'serverEpochTime': 0
    }
