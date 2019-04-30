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
        # TODO: complete device formatting
        'port': device.port,
        'contactDetails': '',
        'username': device.username,
        'password': device.password,
        'ipAddress': device.ipAddress,
        'ne_id': f'{device.ipAddress}:{device.port}',
        'deviceId': device.deviceId,
        'serialNumber': device.deviceId,
        'hostname': f'{device.ipAddress}:{device.port}',
        'platformVersion': '1.7.0.7',
        'status': 'DISCOVERED',
    }
