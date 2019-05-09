from typing import List

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import MyAppMetric
from fog_director_simulator.metrics_collector.my_app import up_status


def collect(db_logic: DatabaseLogic, iterationCount: int, myAppId: int) -> List[MyAppMetric]:
    result = [
        MyAppMetric(  # type: ignore
            iterationCount=iterationCount,
            myAppId=myAppId,
            metricType=up_status.METRIC_TYPE,  # type: ignore
            value=up_status.collect(db_logic=db_logic, iterationCount=iterationCount, myAppId=myAppId),  # type: ignore
        )
    ]
    db_logic.create(*result)

    return result
