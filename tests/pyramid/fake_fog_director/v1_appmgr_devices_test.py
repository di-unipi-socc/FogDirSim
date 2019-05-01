from typing import Any
from typing import Dict

import pytest
from webtest import TestApp

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database import Device


@pytest.fixture
def formatted_device(device: Device) -> Dict[str, Any]:
    return {
        'port': device.port,
        'ipAddress': device.ipAddress,
        'password': device.password,
        'username': device.username,
        'usedCPU': 0,
        'usedMEM': 0,
        'apps': [],
    }


def test_get_v1_appmgr_devices_without_token(testapp):
    # type: (TestApp) -> None
    response = testapp.get('/api/v1/appmgr/devices', expect_errors=True)
    assert response.status_code == 400


def test_get_v1_appmgr_devices_no_devices(testapp):
    # type: (TestApp) -> None
    response = testapp.get(
        '/api/v1/appmgr/devices',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.status_code == 200
    assert response.json == {'data': []}


def test_get_v1_appmgr_devices_with_devices(testapp, database_logic, device, formatted_device):
    # type: (TestApp, DatabaseLogic, Device, Dict[str, Any]) -> None
    database_logic.create(device)
    response = testapp.get(
        '/api/v1/appmgr/devices',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.status_code == 200
    assert response.json == {'data': [formatted_device]}


def test_post_v1_appmgr_devices_without_token(testapp):
    # type: (TestApp) -> None
    response = testapp.post('/api/v1/appmgr/devices', expect_errors=True)
    assert response.status_code == 400


def test_post_v1_appmgr_devices_not_registered_device(testapp):
    # type: (TestApp) -> None
    response = testapp.post_json(
        '/api/v1/appmgr/devices',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params={
            'ipAddress': '1',
            'password': '1',
            'port': '1',
            'username': '1',
        },
    )
    assert response.status_code == 400


def test_post_v1_appmgr_devices_with_registered_device(testapp, database_logic, device, formatted_device):
    # type: (TestApp, DatabaseLogic, Device, Dict[str, Any]) -> None
    params = {
        'ipAddress': device.ipAddress,
        'password': device.password,
        'port': device.port,
        'username': device.username,
    }
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


def test_post_v1_appmgr_devices_with_already_registered_device(testapp, database_logic, device, formatted_device):
    # type: (TestApp, DatabaseLogic, Device, Dict[str, Any]) -> None
    params = {
        'ipAddress': device.ipAddress,
        'password': device.password,
        'port': device.port,
        'username': device.username,
    }
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
