from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config


@view_config(route_name='api.v1.appmgr.tokenservice.token', request_method='DELETE')
def delete_v1_appmgr_tokenservice_token(request: Request) -> Dict[str, Any]:
    raise NotImplementedError()
