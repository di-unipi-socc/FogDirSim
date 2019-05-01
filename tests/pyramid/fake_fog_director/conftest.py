from typing import Any
from typing import Dict

import pytest

from fog_director_simulator.database import Device
from fog_director_simulator.database.models import Application
from fog_director_simulator.database.models import MyApp


@pytest.fixture
def formatted_device(device: Device) -> Dict[str, Any]:
    return {
        'deviceId': device.deviceId,
        'port': device.port,
        'ipAddress': device.ipAddress,
        'password': device.password,
        'username': device.username,
        'usedCPU': 0,
        'usedMEM': 0,
        'apps': [],
    }


@pytest.fixture
def formatted_application(application: Application) -> Dict[str, Any]:
    return {
        'creationDate': -1,
        'localAppId': application.localAppId,
        'version': application.version,
        'published': 'published' if application.isPublished else 'unpublished',
        'profileNeeded': application.profileNeeded.iox_name(),
        'cpuUsage': application.cpuUsage,
        'memoryUsage': application.memoryUsage,
        'sourceAppName': f'{application.localAppId}:{application.version}',
    }


@pytest.fixture
def formatted_my_app(my_app: MyApp) -> Dict[str, Any]:
    return {
        'myAppId': my_app.myAppId,
        'name': my_app.name,
    }
