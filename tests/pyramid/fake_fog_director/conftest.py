from typing import Any
from typing import Dict

import pytest

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
