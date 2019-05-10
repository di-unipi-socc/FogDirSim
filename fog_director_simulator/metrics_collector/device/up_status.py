from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import DeviceMetricType
from fog_director_simulator.metrics_collector import ignore_sqlalchemy_exceptions
from fog_director_simulator.metrics_collector import random_flag


METRIC_TYPE = DeviceMetricType.UP_STATUS


@ignore_sqlalchemy_exceptions(default_return_value=0)
def collect(db_logic: DatabaseLogic, device_id: str) -> float:
    device = db_logic.get_device(deviceId=device_id)
    return 1 if random_flag(
        device.chaosDieProb if device.isAlive else device.chaosReviveProb
    ) else 0
