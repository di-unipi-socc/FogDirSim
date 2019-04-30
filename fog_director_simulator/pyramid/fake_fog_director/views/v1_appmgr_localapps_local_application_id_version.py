from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config


@view_config(route_name='api.v1.appmgr.localapps.local_application_id_version', request_method='PUT')
def put_v1_appmgr_localapps_local_application_id_version(request: Request) -> Dict[str, Any]:
    raise NotImplementedError()
