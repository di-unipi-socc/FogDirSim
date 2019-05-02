from typing import Any
from typing import List

from mypy_extensions import TypedDict

from fog_director_simulator.database.models import Alert
from fog_director_simulator.database.models import Application
from fog_director_simulator.database.models import Device
from fog_director_simulator.database.models import Job
from fog_director_simulator.database.models import MyApp


class AlertApi(TypedDict):
    deviceId: str
    ipAddress: str
    appName: str
    type: str
    message: str
    time: int


class AlertsResponse(TypedDict):
    data: List[AlertApi]


def alert_format(alert: Alert) -> AlertApi:
    return AlertApi(
        appName=alert.myApp.name,
        ipAddress=alert.device.ipAddress,
        message=alert.type.value,
        deviceId=alert.deviceId,
        type=alert.type.name,
        time=alert.time,
    )


class DeviceApi(TypedDict):
    deviceId: str
    port: str
    ipAddress: str
    username: str
    password: str
    usedCPU: int
    usedMEM: int
    apps: List[Any]  # TODO: fix this


class DeviceResponse(TypedDict):
    data: List[DeviceApi]


def device_format(device: Device) -> DeviceApi:
    return DeviceApi(
        deviceId=device.deviceId,
        port=device.port,
        ipAddress=device.ipAddress,
        username=device.username,
        password=device.password,
        # TODO: Extract the fields
        usedCPU=0,
        usedMEM=0,
        apps=[],
    )


class ApplicationApi(TypedDict):
    creationDate: int
    localAppId: str
    version: str
    published: str
    profileNeeded: str
    cpuUsage: float
    memoryUsage: float
    sourceAppName: str


class ApplicationResponse(TypedDict):
    data: List[ApplicationApi]


def application_format(application: Application) -> ApplicationApi:
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


class MyAppApi(TypedDict):
    myAppId: int
    name: str


def myapp_format(my_app: MyApp) -> MyAppApi:
    return MyAppApi(
        myAppId=my_app.myAppId,
        name=my_app.name,
    )


class JobApi(TypedDict):
    jobId: str


def job_format(job: Job) -> JobApi:
    return JobApi(jobId=str(job.jobId))


class TokenServiceApi(TypedDict):
    token: str
    expiryTime: int
    serverEpochTime: int
