from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.database import Device


def _format(device: Device) -> Dict[str, Any]:
    return {
        # TODO: complete device formatting
        'port': device.port,
        'contactDetails': '',
        'username': device.username,
        'password': device.password,
        'ipAddress': device.ipAddress,
        'ne_id': f'{device.ipAddress}:{device.port}',
        'deviceId': device.deviceId,
        'serialNumber': device.deviceId,
        'hostname': f'{device.ipAddress}:{device.port}',
        'platformVersion': '1.7.0.7',
        'status': 'DISCOVERED',
    }


@view_config(route_name='api.v1.appmgr.devices', request_method='GET')
def get_v1_appmgr_devices(request: Request) -> Dict[str, Any]:
    return {
        'data': [
            _format(alert)
            for alert in request.database_logic.get_devices(limit=request.swagger_data['limit'], offset=request.swagger_data['offset'])
        ]
    }


@view_config(route_name='api.v1.appmgr.devices', request_method='POST')
def post_v1_appmgr_devices(request: Request) -> Dict[str, Any]:
    raise NotImplementedError()
