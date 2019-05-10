from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database import DeviceMetricType
from fog_director_simulator.metrics_collector import ignore_sqlalchemy_exceptions


METRIC_TYPE = DeviceMetricType.APPS


@ignore_sqlalchemy_exceptions(default_return_value=0)
def collect(db_logic: DatabaseLogic, device_id: str) -> float:
    # return len(db_logic.get_device(deviceId=device_id).installedApps)
    # FIXME: this is important for the metrics and MUST be fixed
    return 0
