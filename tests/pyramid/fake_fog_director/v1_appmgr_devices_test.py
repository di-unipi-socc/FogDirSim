import typing

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database import Device
from fog_director_simulator.pyramid.fake_fog_director.formatters import DeviceApi
from fog_director_simulator.pyramid.fake_fog_director.request_types import DeviceMinimal

if typing.TYPE_CHECKING:
    from webtest import TestApp


def test_get_v1_appmgr_devices_without_token(testapp: 'TestApp') -> None:
    response = testapp.get('/api/v1/appmgr/devices', expect_errors=True)
    assert response.status_code == 400


def test_get_v1_appmgr_devices_no_devices(testapp: 'TestApp') -> None:
    response = testapp.get(
        '/api/v1/appmgr/devices',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.status_code == 200
    assert response.json == {'data': []}


def test_get_v1_appmgr_devices_with_devices(testapp: 'TestApp', database_logic: DatabaseLogic, device: Device, formatted_device: DeviceApi) -> None:
    database_logic.create(device)
    response = testapp.get(
        '/api/v1/appmgr/devices',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.status_code == 200
    assert response.json == {'data': [formatted_device]}


def test_post_v1_appmgr_devices_without_token(testapp: 'TestApp') -> None:
    response = testapp.post('/api/v1/appmgr/devices', expect_errors=True)
    assert response.status_code == 400


def test_post_v1_appmgr_devices_not_registered_device(testapp: 'TestApp') -> None:
    response = testapp.post_json(
        '/api/v1/appmgr/devices',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params=DeviceMinimal(
            ipAddress='1',
            password='1',
            port='1',
            username='1',
        ),
    )
    assert response.status_code == 400


def test_post_v1_appmgr_devices_with_registered_device(testapp: 'TestApp', database_logic: DatabaseLogic, device: Device, formatted_device: DeviceApi) -> None:
    params = DeviceMinimal(
        ipAddress=device.ipAddress,
        password=device.password,
        port=device.port,
        username=device.username,
    )

    database_logic.create(device)

    response = testapp.post_json(
        '/api/v1/appmgr/devices',
        headers={
            'X-Token-Id': 'token',
        },
        params=params,
    )

    assert response.status_code == 200
    assert response.json == formatted_device


def test_post_v1_appmgr_devices_with_already_registered_device(testapp: 'TestApp', database_logic: DatabaseLogic, device: Device, formatted_device: DeviceApi) -> None:
    params = DeviceMinimal(
        ipAddress=device.ipAddress,
        password=device.password,
        port=device.port,
        username=device.username,
    )

    device.timeOfCreation = 0
    database_logic.create(device)

    response = testapp.post_json(
        '/api/v1/appmgr/devices',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params=params,
    )

    assert response.status_code == 409
