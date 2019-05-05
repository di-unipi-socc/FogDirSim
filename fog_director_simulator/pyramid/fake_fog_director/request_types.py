from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from mypy_extensions import TypedDict


class ApplicationResourceAsk(TypedDict):
    cpu: int
    memory: int
    profile: str
    network: List[Dict[str, Any]]


class ResourceAsk(TypedDict):
    resources: ApplicationResourceAsk


class MyAppActionDeployItem(TypedDict):
    deviceId: str
    resourceAsk: ResourceAsk


class MyAppActionDeployDevices(TypedDict):
    config: Dict[str, Any]
    metricsPollingFrequency: str
    startApp: bool
    devices: List[MyAppActionDeployItem]


class MyAppActionUndeployDevices(TypedDict):
    devices: List[str]


class MyAppAction(TypedDict, total=False):
    deploy: Optional[MyAppActionDeployDevices]
    start: Optional[Dict[str, Any]]
    stop: Optional[Dict[str, Any]]
    undeploy: Optional[MyAppActionUndeployDevices]


class DeviceMinimal(TypedDict):
    port: str
    ipAddress: str
    username: str
    password: str


class LocalApp(TypedDict):
    cpuUsage: int
    creationDate: int
    localAppId: str
    memoryUsage: int
    profileNeeded: str
    published: str
    sourceAppName: str
    version: str


class DeployMyApp(TypedDict):
    appSourceType: str
    name: str
    sourceAppName: str
    version: str
