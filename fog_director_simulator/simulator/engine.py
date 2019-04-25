from functools import partial
from typing import Callable
from typing import Dict
from typing import Mapping

from fog_director_simulator import database
from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database import Device
from fog_director_simulator.database.models import Alert
from fog_director_simulator.database.models import AlertType
from fog_director_simulator.database.models import DeviceMetric
from fog_director_simulator.database.models import DeviceMetricType
from fog_director_simulator.database.models import DeviceSampling
from fog_director_simulator.database.models import Job
from fog_director_simulator.database.models import JobMetric
from fog_director_simulator.database.models import JobMetricType
from fog_director_simulator.database.models import JobStatus
from fog_director_simulator.database.models import MyApp
from fog_director_simulator.database.models import MyAppAlertStatistic
from fog_director_simulator.database.models import MyAppMetric
from fog_director_simulator.database.models import MyAppMetricType
from fog_director_simulator.metrics_collector import device
from fog_director_simulator.metrics_collector import job
from fog_director_simulator.metrics_collector import my_app


def _send_alert(db_logic: DatabaseLogic, iterationCount: int, job: Job, device: Device, alert_type: AlertType) -> None:
    my_app_statistics = db_logic.get_my_app_alert_statistics(myApp=job.myApp, alert_type=alert_type)
    alert_count = my_app_statistics.count if my_app_statistics else 0

    alerts_to_create = [
        MyAppAlertStatistic(
            myApp=job.myApp,
            type=alert_type,
            count=alert_count + 1,
        ),
    ]
    if alert_type != AlertType.NO_ALERT:
        alerts_to_create.append(
            Alert(
                myApp=job.myApp,
                device=device,
                type=alert_type,
                time=iterationCount,
            ),
        )

    db_logic.create(*alerts_to_create)


def _alert_not_alive_device(send_alert: Callable[[AlertType], None]) -> bool:
    send_alert(AlertType.DEVICE_REACHABILITY)

    return True


def _maybe_alert_alive_device(
    send_alert: Callable[[AlertType], None],
    job_metrics: Dict[JobMetricType, JobMetric],
    device: Device,
    device_metrics: Dict[DeviceMetricType, DeviceMetric],
) -> bool:

    if device.reservedCPU > device_metrics[DeviceMetricType.CPU].value:
        send_alert(AlertType.APP_HEALTH)
        return True

    if not job_metrics[JobMetricType.ENOUGH_CPU].value:
        send_alert(AlertType.CPU_CRITICAL_CONSUMPTION)
        return True

    if device.reservedMEM > device_metrics[DeviceMetricType.MEM].value:
        send_alert(AlertType.APP_HEALTH)
        return True

    if not job_metrics[JobMetricType.ENOUGH_MEM].value:
        send_alert(AlertType.MEM_CRITICAL_CONSUMPTION)
        return True

    return False


class Simulator:

    def __init__(self, database_config: database.Config):
        self.database_client = database.DatabaseClient(database_config)
        self.iteration_count = 0
        self.is_alive = True

    def _evaluate_device_metrics(self) -> Dict[Device, Dict[DeviceMetricType, DeviceMetric]]:
        with self.database_client as db_logic:
            metrics = {
                current_device: {
                    device_metric.metricType: device_metric
                    for device_metric in device.collect(
                        iterationCount=self.iteration_count,
                        db_logic=db_logic,
                        device_id=current_device.deviceId,
                    )
                }
                for current_device in db_logic.get_all_devices()
            }
            # Save all the metrics on the db
            db_logic.create(
                metric
                for metrics_mapping in metrics.values()
                for metric in metrics_mapping.values()
            )

            return metrics

    def _evaluate_job_metrics(self) -> Dict[Job, Dict[JobMetricType, JobMetric]]:
        with self.database_client as db_logic:
            metrics = {
                current_job: {
                    job_metric.metricType: job_metric
                    for job_metric in job.collect(
                        iterationCount=self.iteration_count,
                        db_logic=db_logic,
                        jobId=current_job.jobId,
                    )
                }
                for current_job in db_logic.get_all_jobs()
            }
            # Save all the metrics on the db
            db_logic.create(
                metric
                for metrics_mapping in metrics.values()
                for metric in metrics_mapping.values()
            )

            return metrics

    def _evaluate_my_app_metrics(self) -> Dict[MyApp, Dict[MyAppMetricType, MyAppMetric]]:
        with self.database_client as db_logic:
            metrics = {
                current_my_apps: {
                    my_app_metric.metricType: my_app_metric
                    for my_app_metric in my_app.collect(
                        iterationCount=self.iteration_count,
                        db_logic=db_logic,
                        myAppId=current_my_apps.myAppId,
                    )
                }
                for current_my_apps in db_logic.get_all_my_apps()
            }
            # Save all the metrics on the db
            db_logic.create(
                metric
                for metrics_mapping in metrics.values()
                for metric in metrics_mapping.values()
            )

            return metrics

    def _evaluate_device_sampling(
        self,
        db_logic: DatabaseLogic,
        device: Device,
        device_metrics: Mapping[Device, Dict[DeviceMetricType, DeviceMetric]],
        job_metrics: Mapping[Job, Dict[JobMetricType, JobMetric]],
        my_app_metrics: Mapping[MyApp, Dict[MyAppMetricType, MyAppMetric]],
    ) -> DeviceSampling:
        device_lifetime = (device.timeOfRemoval or self.iteration_count) - device.timeOfCreation

        cpu_metrics = db_logic.get_device_metrics(deviceId=device.deviceId, metricType=DeviceMetricType.CPU)
        mem_metrics = db_logic.get_device_metrics(deviceId=device.deviceId, metricType=DeviceMetricType.MEM)
        myapps_metrics = db_logic.get_device_metrics(deviceId=device.deviceId, metricType=DeviceMetricType.APPS)

        instants_cpu_critical = sum(
            1
            for metric in cpu_metrics
            if metric.value >= 0.95 * device.totalCPU
        )
        instants_mem_critical = sum(
            1
            for metric in mem_metrics
            if metric.value >= 0.95 * device.totalMEM
        )

        used_cpu_ticks = sum(metric.value for metric in cpu_metrics)
        used_mem_ticks = sum(metric.value for metric in mem_metrics)

        installed_my_apps_instants = sum(metric.value for metric in myapps_metrics)

        return DeviceSampling(
            iterationCount=self.iteration_count,
            deviceId=device.deviceId,
            criticalCpuPercentage=instants_cpu_critical / device_lifetime,
            criticalMemPercentage=instants_mem_critical / device_lifetime,
            averageCpuUsed=used_cpu_ticks / device_lifetime,
            averageMemUsed=used_mem_ticks / device_lifetime,
            averageMyAppCount=installed_my_apps_instants / device_lifetime,
        )

    def _evaluate_samplings(
        self,
        device_metrics: Mapping[Device, Dict[DeviceMetricType, DeviceMetric]],
        job_metrics: Mapping[Job, Dict[JobMetricType, JobMetric]],
        my_app_metrics: Mapping[MyApp, Dict[MyAppMetricType, MyAppMetric]],
    ) -> Dict[Device, DeviceSampling]:
        with self.database_client as db_logic:
            metrics = {
                iteration_device: self._evaluate_device_sampling(
                    db_logic=db_logic,
                    device=iteration_device,
                    device_metrics=device_metrics,
                    job_metrics=job_metrics,
                    my_app_metrics=my_app_metrics,
                )
                for iteration_device in device_metrics
            }
            # Save all the metrics on the db
            db_logic.create(metric for metric in metrics.values())

            return metrics

    def _handle_alerts(
        self,
        db_logic: DatabaseLogic,
        device_metrics: Mapping[Device, Dict[DeviceMetricType, DeviceMetric]],
        job_metrics: Mapping[Job, Dict[JobMetricType, JobMetric]],
        my_app_metrics: Mapping[MyApp, Dict[MyAppMetricType, MyAppMetric]],
    ) -> None:
        for current_job, current_job_metrics in job_metrics.items():
            if current_job.status is not JobStatus.START:
                continue
            for current_device in current_job.devices:
                send_alert = partial(
                    _send_alert,
                    db_logic=db_logic,
                    iterationCount=self.iteration_count,
                    job=job,
                    device=device,
                )

                if current_device.isAlive:
                    created_alert = _maybe_alert_alive_device(
                        send_alert=send_alert,
                        job_metrics=current_job_metrics[current_job],
                        device=current_device,
                        device_metrics=device_metrics[current_device],
                    )
                else:
                    created_alert = _alert_not_alive_device(send_alert=send_alert)

                if not created_alert:
                    send_alert(AlertType.NO_ALERT)

    def run(self) -> None:
        while self.is_alive:
            with self.database_client as db_logic:
                self.iteration_count += 1
                device_metrics = self._evaluate_device_metrics()
                job_metrics = self._evaluate_job_metrics()
                my_app_metrics = self._evaluate_my_app_metrics()

                # Evaluate pre-aggregated metrics to simplify front-end efforts
                # for data retrieval (no need to run a lot of queries all the time)
                # and to provide information about the current state of the simulation
                # (NOTE: this is an hack ... but we're ok-ish for now with this)
                self._evaluate_samplings(
                    device_metrics=device_metrics,
                    job_metrics=job_metrics,
                    my_app_metrics=my_app_metrics,
                )

                self._handle_alerts(
                    db_logic=db_logic,
                    device_metrics=device_metrics,
                    job_metrics=job_metrics,
                    my_app_metrics=my_app_metrics,
                )

                # FIXME: Update device status ... if the device is dead ... what has to be done on the db?


if __name__ == '__main__':
    Simulator(database_config=database.Config()).run()
