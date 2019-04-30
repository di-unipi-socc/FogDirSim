from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config


@view_config(route_name='api.v1.appmgr.devices.device_id', request_method='DELETE')
def delete_v1_appmgr_devices_device_id(request: Request) -> Dict[str, Any]:
    raise NotImplementedError()
