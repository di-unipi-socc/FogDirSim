from typing import List

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import DeviceMetric
from fog_director_simulator.metrics_collector.device import apps
from fog_director_simulator.metrics_collector.device import cpu
from fog_director_simulator.metrics_collector.device import energy
from fog_director_simulator.metrics_collector.device import memory
from fog_director_simulator.metrics_collector.device import up_status


def collect(db_logic: DatabaseLogic, iterationCount: int, device_id: str) -> List[DeviceMetric]:
    result = [
        DeviceMetric(  # type: ignore
            iterationCount=iterationCount,
            deviceId=device_id,
            metricType=apps.METRIC_TYPE,  # type: ignore
            value=apps.collect(db_logic=db_logic, device_id=device_id),  # type: ignore
        ),
        DeviceMetric(  # type: ignore
            iterationCount=iterationCount,
            deviceId=device_id,
            metricType=cpu.METRIC_TYPE,  # type: ignore
            value=cpu.collect(db_logic=db_logic, device_id=device_id),  # type: ignore
        ),
        DeviceMetric(  # type: ignore
            iterationCount=iterationCount,
            deviceId=device_id,
            metricType=memory.METRIC_TYPE,  # type: ignore
            value=memory.collect(db_logic=db_logic, device_id=device_id),  # type: ignore
        ),
        DeviceMetric(  # type: ignore
            iterationCount=iterationCount,
            deviceId=device_id,
            metricType=up_status.METRIC_TYPE,  # type: ignore
            value=up_status.collect(db_logic=db_logic, device_id=device_id),  # type: ignore
        ),
    ]
    db_logic.create(*result)

    energy_metric = DeviceMetric(  # type: ignore
        iterationCount=iterationCount,
        deviceId=device_id,
        metricType=energy.METRIC_TYPE,  # type: ignore
        value=energy.collect(db_logic=db_logic, iterationCount=iterationCount, device_id=device_id),  # type: ignore
    )
    db_logic.create(energy_metric)

    result.append(energy_metric)
    return result
