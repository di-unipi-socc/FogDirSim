from webtest import TestApp

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database import Device


def test_v1_appmgr_devices_without_token(testapp):
    # type: (TestApp) -> None
    response = testapp.get('/api/v1/appmgr/devices', expect_errors=True)
    assert response.status_code == 400


def test_v1_appmgr_devices_no_devices(testapp):
    # type: (TestApp) -> None
    response = testapp.get(
        '/api/v1/appmgr/devices',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.status_code == 200
    assert response.json == {'data': []}


def test_v1_appmgr_devices_with_devices(testapp, database_logic, device):
    # type: (TestApp, DatabaseLogic, Device) -> None
    database_logic.create(device)
    response = testapp.get(
        '/api/v1/appmgr/devices',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.status_code == 200
    assert response.json == {
        'data': [
            {
                'contactDetails': '',
                'deviceId': 'deviceId',
                'hostname': 'ipAddress:1',
                'ipAddress': 'ipAddress',
                'ne_id': 'ipAddress:1',
                'password': 'password',
                'platformVersion': '1.7.0.7',
                'port': '1',
                'serialNumber': 'deviceId',
                'status': 'DISCOVERED',
                'username': 'username',
            },
        ],
    }
