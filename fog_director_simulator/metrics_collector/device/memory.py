from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database import DeviceMetricType
from fog_director_simulator.metrics_collector import ignore_sqlalchemy_exceptions
from fog_director_simulator.metrics_collector import random_sample


METRIC_TYPE = DeviceMetricType.MEM


@ignore_sqlalchemy_exceptions(default_return_value=0)
def collect(db_logic: DatabaseLogic, device_id: str) -> float:
    with db_logic:
        device = db_logic.get_device(deviceId=device_id)
        return random_sample(
            mean=device.memMetricsDistribution.mean,
            std_deviation=device.memMetricsDistribution.std_deviation,
            lower_bound=0,
            upper_bound=device.totalMEM,
        )
