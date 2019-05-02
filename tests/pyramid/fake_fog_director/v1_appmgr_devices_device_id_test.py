from webtest import TestApp

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import Device
from fog_director_simulator.pyramid.fake_fog_director.formatters import DeviceApi


def test_delete_v1_appmgr_devices_device_id_without_tokens(testapp: TestApp) -> None:
    response = testapp.delete('/api/v1/appmgr/devices/{device_id}', expect_errors=True)
    assert response.status_code == 400


def test_delete_v1_appmgr_devices_device_id_not_registered_device(testapp: TestApp) -> None:
    response = testapp.delete(
        '/api/v1/appmgr/devices/1',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.status_code == 404


def test_delete_v1_appmgr_devices_device_id_with_registered_device(testapp: TestApp, database_logic: DatabaseLogic, device: Device, formatted_device: DeviceApi) -> None:
    device_id = device.deviceId
    database_logic.create(device)

    response = testapp.delete(
        f'/api/v1/appmgr/devices/{device_id}',
        headers={
            'X-Token-Id': 'token',
        },
    )

    assert response.status_code == 200
    assert response.json == formatted_device
