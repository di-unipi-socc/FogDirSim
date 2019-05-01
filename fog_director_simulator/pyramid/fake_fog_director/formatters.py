from typing import Any
from typing import Dict

from fog_director_simulator.database.models import Alert
from fog_director_simulator.database.models import Application
from fog_director_simulator.database.models import Device
from fog_director_simulator.database.models import Job
from fog_director_simulator.database.models import MyApp


def alert_format(alert: Alert) -> Dict[str, Any]:
    return {
        'myAppId': alert.myAppId,
        'deviceId': alert.deviceId,
        'type': alert.type.name,
        'time': alert.time,
    }


def device_format(device: Device) -> Dict[str, Any]:
    return {
        'deviceId': device.deviceId,
        'port': device.port,
        'ipAddress': device.ipAddress,
        'username': device.username,
        'password': device.password,
        # TODO: Extract the fields
        'usedCPU': 0,
        'usedMEM': 0,
        'apps': [],
    }


def application_format(application: Application) -> Dict[str, Any]:
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


def myapp_format(my_app: MyApp) -> Dict[str, Any]:
    return {
        'myAppId': my_app.myAppId,
        'name': my_app.name,
    }


def job_format(job: Job) -> Dict[str, Any]:
    return {
        'jobId': str(job.jobId),
    }
