from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import JobMetricType
from fog_director_simulator.database.models import JobStatus


METRIC_TYPE = JobMetricType.UP_STATUS


def collect(db_logic: DatabaseLogic, job_id: int) -> float:
    job = db_logic.get_job(jobId=job_id)
    return 1 if job.status == JobStatus.START else 0
