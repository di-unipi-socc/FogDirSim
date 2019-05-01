from typing import Any
from typing import Dict

from fog_director_simulator.database import Alert
from fog_director_simulator.database import Device


def alert_format(alert: Alert) -> Dict[str, Any]:
    return {
        'myAppId': alert.myAppId,
        'deviceId': alert.deviceId,
        'type': alert.type.name,
        'time': alert.time,
    }


def device_format(device: Device) -> Dict[str, Any]:
    return {
        'port': device.port,
        'ipAddress': device.ipAddress,
        'username': device.username,
        'password': device.password,
        # TODO: Extract the fields
        'usedCPU': 0,
        'usedMEM': 0,
        'apps': [],
    }
