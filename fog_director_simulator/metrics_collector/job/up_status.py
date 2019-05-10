from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import JobMetricType
from fog_director_simulator.database.models import JobStatus
from fog_director_simulator.metrics_collector import ignore_sqlalchemy_exceptions


METRIC_TYPE = JobMetricType.UP_STATUS


@ignore_sqlalchemy_exceptions(default_return_value=0)
def collect(db_logic: DatabaseLogic, job_id: int) -> float:
    job = db_logic.get_job(jobId=job_id)
    return 1 if job.status == JobStatus.START else 0
