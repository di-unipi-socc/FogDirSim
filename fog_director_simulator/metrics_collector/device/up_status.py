from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import DeviceMetricType
from fog_director_simulator.metrics_collector import random_flag


METRIC_TYPE = DeviceMetricType.UP_STATUS


def collect(db_logic: DatabaseLogic, device_id: str) -> bool:
    device = db_logic.get_device(device_id=device_id)
    return random_flag(
        device.chaos_die_prob if device.alive else device.chaos_revive_prob
    )
