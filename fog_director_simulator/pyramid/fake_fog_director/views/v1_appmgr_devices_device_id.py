from typing import Any
from typing import Dict

from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.pyramid.fake_fog_director.formatters import device_format


@view_config(route_name='api.v1.appmgr.devices.device_id', request_method='DELETE')
def delete_v1_appmgr_devices_device_id(request: Request) -> Dict[str, Any]:
    device = request.database_logic.get_device(
        deviceId=request.swagger_data['device_id'],
    )
    if device is None:
        raise HTTPNotFound

    device.timeOfRemoval = request.simulation_time
    formatted_device = device_format(device)

    return formatted_device
