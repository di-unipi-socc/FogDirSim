from typing import List

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import MyAppMetric
from fog_director_simulator.metrics_collector.my_app import up_status


def collect(db_logic: DatabaseLogic, iterationCount: int, myAppId: int) -> List[MyAppMetric]:
    return [
        MyAppMetric(  # type: ignore
            iterationCount=iterationCount,
            myAppId=myAppId,
            metricType=mod.METRIC_TYPE,  # type: ignore
            value=mod.collect(db_logic=db_logic, iterationCount=iterationCount, myAppId=myAppId),  # type: ignore
        )
        for mod in (up_status, )
    ]
