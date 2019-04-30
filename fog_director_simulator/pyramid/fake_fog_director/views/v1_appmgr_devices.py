from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.pyramid.fake_fog_director.formatters import device_format


@view_config(route_name='api.v1.appmgr.devices', request_method='GET')
def get_v1_appmgr_devices(request: Request) -> Dict[str, Any]:
    return {
        'data': [
            device_format(alert)
            for alert in request.database_logic.get_devices(limit=request.swagger_data['limit'], offset=request.swagger_data['offset'])
        ]
    }


@view_config(route_name='api.v1.appmgr.devices', request_method='POST')
def post_v1_appmgr_devices(request: Request) -> Dict[str, Any]:
    raise NotImplementedError()
