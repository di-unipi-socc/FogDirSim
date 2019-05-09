from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import JobMetricType
from fog_director_simulator.database.models import JobStatus


METRIC_TYPE = JobMetricType.ENOUGH_CPU


def collect(db_logic: DatabaseLogic, job_id: int) -> float:
    # Local import to prevent circular import
    from fog_director_simulator.metrics_collector.job import scaled_random_sample

    job = db_logic.get_job(jobId=job_id)
    myApp = db_logic.get_my_app(myAppId=job.myAppId)
    application = db_logic.get_application(localAppId=myApp.applicationLocalAppId, version=myApp.applicationVersion)

    for job_device_allocation in job.job_device_allocations:  # type: ignore
        reserved_cpu = job_device_allocation.cpu
        required_cpu = application.cpuUsage

        current_cpu_usage = scaled_random_sample(
            job_intensivity=job.profile,
            scale_factor=required_cpu,
            upper_bound=reserved_cpu if job.status == JobStatus.START else 0,
        )

        if reserved_cpu < current_cpu_usage:
            return 0

    return 1
