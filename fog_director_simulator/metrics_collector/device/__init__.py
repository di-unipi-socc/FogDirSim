from typing import List

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import DeviceMetric
from fog_director_simulator.metrics_collector.device import apps
from fog_director_simulator.metrics_collector.device import cpu
from fog_director_simulator.metrics_collector.device import energy
from fog_director_simulator.metrics_collector.device import memory
from fog_director_simulator.metrics_collector.device import up_status


def collect(db_logic: DatabaseLogic, iterationCount: int, device_id: str) -> List[DeviceMetric]:
    return [
        DeviceMetric(  # type: ignore
            iterationCount=iterationCount,
            deviceId=device_id,
            metricType=mod.METRIC_TYPE,  # type: ignore
            value=mod.collect(db_logic=db_logic, device_id=device_id),  # type: ignore
        )
        for mod in (apps, cpu, memory, up_status, energy)
    ]
