from enum import Enum
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


class DeviceCapabilityNodeDetailApi(TypedDict):
    available: float
    total: float


class DeviceCapabilityNodeApi(TypedDict):
    cpu: DeviceCapabilityNodeDetailApi
    memory: DeviceCapabilityNodeDetailApi


class DeviceCapabilityNodesApi(TypedDict):
    nodes: List[DeviceCapabilityNodeApi]


class DeviceResponseApi(TypedDict):
    apps: List[Any]  # TODO: fix this
    capabilities: DeviceCapabilityNodesApi
    ipAddress: str
    deviceId: str
    port: str
    usedCPU: float
    usedMEM: float
    username: str


class DeviceResponse(TypedDict):
    data: List[DeviceResponseApi]


class _DeviceCapabilityNodDetailType(Enum):
    CPU = 1
    MEM = 2


def device_capability_node_detail_format(device: Device, detail_type: _DeviceCapabilityNodDetailType) -> DeviceCapabilityNodeDetailApi:
    if detail_type == _DeviceCapabilityNodDetailType.CPU:
        return DeviceCapabilityNodeDetailApi(
            available=device.totalCPU - device.reservedCPU,
            total=device.totalCPU,
        )
    elif detail_type == _DeviceCapabilityNodDetailType.MEM:
        return DeviceCapabilityNodeDetailApi(
            available=device.totalMEM - device.reservedMEM,
            total=device.totalMEM,
        )
    else:
        raise RuntimeError('Impossible getting here')


def device_capability_node_format(device: Device) -> DeviceCapabilityNodeApi:
    return DeviceCapabilityNodeApi(
        cpu=device_capability_node_detail_format(device, _DeviceCapabilityNodDetailType.CPU),
        memory=device_capability_node_detail_format(device, _DeviceCapabilityNodDetailType.MEM),
    )


def device_capability_nodes_format(device: Device) -> DeviceCapabilityNodesApi:
    return DeviceCapabilityNodesApi(
        nodes=[device_capability_node_format(device)],
    )


def device_format(device: Device) -> DeviceResponseApi:
    return DeviceResponseApi(
        apps=[],  # TODO: fix this
        capabilities=device_capability_nodes_format(device),
        deviceId=device.deviceId,
        ipAddress=device.ipAddress,
        port=device.port,
        usedCPU=device.reservedCPU,  # TODO: fix it with samplings
        usedMEM=device.reservedMEM,  # TODO: fix it with samplings
        username=device.username,
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
