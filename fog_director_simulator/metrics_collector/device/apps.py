from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database import DeviceMetricType


METRIC_TYPE = DeviceMetricType.APPS


def collect(db_logic: DatabaseLogic, device_id: str) -> float:
    # return len(db_logic.get_device(deviceId=device_id).installedApps)
    # FIXME: this is important for the metrics and MUST be fixed
    return 0
