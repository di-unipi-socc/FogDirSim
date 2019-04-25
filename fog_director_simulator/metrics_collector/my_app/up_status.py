from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import JobMetricType
from fog_director_simulator.database.models import MyAppMetricType


METRIC_TYPE = MyAppMetricType.UP_STATUS


def collect(db_logic: DatabaseLogic, iterationCount: int, myAppId: str) -> bool:
    min_replicas = db_logic.get_my_app(my_app_id=myAppId).minJobReplicas
    jobs = {
        job: (
            db_logic.get_job_metric(iterationCount=iterationCount, job_id=job.jobId, metric_type=JobMetricType.ENOUGH_CPU).value or
            db_logic.get_job_metric(iterationCount=iterationCount, job_id=job.jobId, metric_type=JobMetricType.ENOUGH_MEM).value
        )
        for job in db_logic.get_all_jobs(myAppId=myAppId)
    }

    min_expected_replicas = len(jobs) if min_replicas is None else min_replicas
    return sum(1 for job_has_resources in jobs.values() if job_has_resources) >= min_expected_replicas
