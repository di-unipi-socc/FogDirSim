import pytest

from fog_director_simulator.database import Device
from fog_director_simulator.database.models import Alert
from fog_director_simulator.database.models import Application
from fog_director_simulator.database.models import MyApp
from fog_director_simulator.pyramid.fake_fog_director.formatters import AlertApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import ApplicationApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import DeviceApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import MyAppApi


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
def formatted_device(device: Device) -> DeviceApi:
    return DeviceApi(
        deviceId=device.deviceId,
        port=device.port,
        ipAddress=device.ipAddress,
        password=device.password,
        username=device.username,
        usedCPU=0,
        usedMEM=0,
        apps=[],
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
