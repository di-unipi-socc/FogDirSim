from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import JobMetricType
from fog_director_simulator.database.models import JobStatus
from fog_director_simulator.metrics_collector.job import scaled_random_sample


METRIC_TYPE = JobMetricType.ENOUGH_MEM


def collect(db_logic: DatabaseLogic, job_id: str) -> bool:
    job = db_logic.get_job(job_id=job_id)
    myApp = db_logic.get_my_app(my_app_id=job.myappId)
    application = db_logic.get_application(source_app_name=myApp.sourceAppName)

    for device in job.devices:
        reserved_mem = device.resourceAsk.memory
        required_mem = application.memoryUsage

        current_mem_usage = scaled_random_sample(
            job_intensivity=job.profile,
            scale_factor=required_mem,
            upper_bound=reserved_mem if job.status == JobStatus.START else 0,
        )

        if reserved_mem < current_mem_usage:
            return False

    return True
