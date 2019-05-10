import typing
from itertools import repeat
from unittest import mock

import pytest
from webtest import TestApp

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database import Device
from fog_director_simulator.database.models import Alert
from fog_director_simulator.database.models import Application
from fog_director_simulator.database.models import MyApp
from fog_director_simulator.pyramid.fake_fog_director.formatters import AlertApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import ApplicationApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import DeviceCapabilityNodeApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import DeviceCapabilityNodeDetailApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import DeviceCapabilityNodesApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import DeviceResponseApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import MyAppApi
from fog_director_simulator.pyramid.fake_fog_director.webapp import create_application


@pytest.fixture
def testapp_not_increasing_time(database_logic: DatabaseLogic) -> typing.Generator[TestApp, None, None]:
    create_application.cache_clear()
    database_logic.get_simulation_time.side_effect = repeat(0)  # type: ignore  # the actual database logic is a mock ;)
    yield TestApp(app=create_application())


@pytest.fixture
def testapp(database_logic: DatabaseLogic) -> typing.Generator[TestApp, None, None]:
    create_application.cache_clear()
    with mock.patch('fog_director_simulator.pyramid.sleep', autospec=True):
        yield TestApp(app=create_application())


@pytest.fixture
def formatted_alert(alert: Alert) -> AlertApi:
    return AlertApi(
        appName=alert.myApp.name,
        ipAddress=alert.device.ipAddress,
        message=alert.type.value,
        deviceId=alert.device.deviceId,
        type=alert.type.name,
        time=alert.time,
    )


@pytest.fixture
def formatted_device(device: Device) -> DeviceResponseApi:
    return DeviceResponseApi(
        apps=[],
        capabilities=DeviceCapabilityNodesApi(
            nodes=[
                DeviceCapabilityNodeApi(
                    cpu=DeviceCapabilityNodeDetailApi(available=1, total=2),
                    memory=DeviceCapabilityNodeDetailApi(available=1, total=6),
                )
            ],
        ),
        deviceId=device.deviceId,
        ipAddress=device.ipAddress,
        port=device.port,
        usedCPU=1,
        usedMEM=5,
        username=device.username,
    )


@pytest.fixture
def formatted_application(application: Application) -> ApplicationApi:
    return ApplicationApi(
        creationDate=-1,
        localAppId=application.localAppId,
        version=application.version,
        published='published' if application.isPublished else 'unpublished',
        profileNeeded=application.profileNeeded.iox_name(),
        cpuUsage=application.cpuUsage,
        memoryUsage=application.memoryUsage,
        sourceAppName=f'{application.localAppId}:{application.version}',
    )


@pytest.fixture
def formatted_my_app(my_app: MyApp) -> MyAppApi:
    return MyAppApi(
        myAppId=my_app.myAppId,
        name=my_app.name,
    )
