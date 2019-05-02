from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import DeviceMetricType
from fog_director_simulator.metrics_collector import random_flag


METRIC_TYPE = DeviceMetricType.UP_STATUS


def collect(db_logic: DatabaseLogic, device_id: str) -> bool:
    device = db_logic.get_device(deviceId=device_id)
    return random_flag(
        device.chaosDieProb if device.isAlive else device.chaosReviveProb
    )
