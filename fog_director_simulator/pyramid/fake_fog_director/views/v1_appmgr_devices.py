from typing import cast

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPConflict
from pyramid.request import Request
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

from fog_director_simulator.pyramid.fake_fog_director.formatters import device_format
from fog_director_simulator.pyramid.fake_fog_director.formatters import DeviceApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import DeviceResponse
from fog_director_simulator.pyramid.fake_fog_director.request_types import DeviceMinimal


@view_config(route_name='api.v1.appmgr.devices', request_method='GET')
def get_v1_appmgr_devices(request: Request) -> DeviceResponse:
    return DeviceResponse(
        data=[
            device_format(device)
            for device in request.database_logic.get_devices(limit=request.swagger_data['limit'], offset=request.swagger_data['offset'])
            if device.timeOfRemoval is None or device.timeOfRemoval > request.simulation_time
        ],
    )


@view_config(route_name='api.v1.appmgr.devices', request_method='POST')
def post_v1_appmgr_devices(request: Request) -> DeviceApi:
    body = cast(DeviceMinimal, request.swagger_data['body'])

    try:
        device = request.database_logic.get_device_from_arguments(
            port=body['port'],
            ipAddress=body['ipAddress'],
            username=body['username'],
            password=body['password'],
        )
    except NoResultFound:
        raise HTTPBadRequest()

    if device.timeOfCreation is not None:
        raise HTTPConflict()

    device.timeOfCreation = request.simulation_time
    request.database_logic.create(device)

    return device_format(device)
