import pytest
from sqlalchemy.orm.exc import NoResultFound

from fog_director_simulator.database import DatabaseClient
from fog_director_simulator.database.models import Application
from fog_director_simulator.database.models import Device
from fog_director_simulator.database.models import DeviceMetric
from fog_director_simulator.database.models import Job
from fog_director_simulator.database.models import JobMetric
from fog_director_simulator.database.models import MyApp


def test_create(database: DatabaseClient, device: Device) -> None:
    dict_representation = device.to_dict()
    with database:
        new_device, = database.logic.create(device)
        assert new_device == device
    with database:
        assert dict_representation == database.logic.get_device(deviceId=dict_representation['deviceId']).to_dict()


def test_select_device(database: DatabaseClient, device: Device) -> None:
    with database:
        database.logic.create(device)
        assert device == database.logic.get_device(device.deviceId)
        with pytest.raises(NoResultFound):
            assert database.logic.get_device('not-existing-device')


def test_select_device_metric(database: DatabaseClient, device_metric: DeviceMetric) -> None:
    with database:
        database.logic.create(device_metric)
        assert device_metric == database.logic.get_device_metric(device_metric.iterationCount, device_metric.deviceId, device_metric.metricType)
        with pytest.raises(NoResultFound):
            assert database.logic.get_device_metric(device_metric.iterationCount + 1, device_metric.deviceId, device_metric.metricType) is None


def test_select_job(database: DatabaseClient, job: Job) -> None:
    with database:
        database.logic.create(job)
        assert job == database.logic.get_job(job.jobId)
        with pytest.raises(NoResultFound):
            assert database.logic.get_job('not-existing-job') is None


def test_select_job_metric(database: DatabaseClient, job: Job, job_metric: JobMetric) -> None:
    with database:
        database.logic.create(job, job_metric)
        assert job_metric == database.logic.get_job_metric(job_metric.iterationCount, job_metric.jobId, job_metric.metricType)
        with pytest.raises(NoResultFound):
            assert database.logic.get_job_metric(job_metric.iterationCount + 1, job_metric.jobId, job_metric.metricType) is None


def test_select_application(database: DatabaseClient, application: Application) -> None:
    with database:
        database.logic.create(application)
        assert application == database.logic.get_application(application.localAppId, application.version)
        with pytest.raises(NoResultFound):
            assert database.logic.get_application(application.localAppId, 'a-random-version') is None


def test_select_my_app(database: DatabaseClient, my_app: MyApp) -> None:
    with database:
        database.logic.create(my_app)
        assert my_app == database.logic.get_my_app(my_app.myAppId)
        with pytest.raises(NoResultFound):
            assert database.logic.get_my_app(myAppId='not-existing-myApp') is None
