from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import JobMetricType
from fog_director_simulator.database.models import MyAppMetricType
from fog_director_simulator.metrics_collector import ignore_sqlalchemy_exceptions


METRIC_TYPE = MyAppMetricType.UP_STATUS


@ignore_sqlalchemy_exceptions(default_return_value=0)
def collect(db_logic: DatabaseLogic, iterationCount: int, myAppId: int) -> float:
    with db_logic:
        min_replicas = db_logic.get_my_app(myAppId=myAppId).minJobReplicas
        jobs = {
            job: (
                db_logic.get_job_metric(iterationCount=iterationCount, jobId=job.jobId, metricType=JobMetricType.ENOUGH_CPU).value or
                db_logic.get_job_metric(iterationCount=iterationCount, jobId=job.jobId, metricType=JobMetricType.ENOUGH_MEM).value
            )
            for job in db_logic.get_all_jobs(myAppId=myAppId)
        }

        min_expected_replicas = len(jobs) if min_replicas is None else min_replicas
        return 1 if sum(1 for job_has_resources in jobs.values() if job_has_resources) >= min_expected_replicas else 0
