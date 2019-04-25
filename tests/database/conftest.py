import pytest

from fog_director_simulator.database import Config
from fog_director_simulator.database import DatabaseClient
from fog_director_simulator.database.models import Application
from fog_director_simulator.database.models import ApplicationProfile
from fog_director_simulator.database.models import Device
from fog_director_simulator.database.models import DeviceMetric
from fog_director_simulator.database.models import DeviceMetricType
from fog_director_simulator.database.models import DeviceSampling
from fog_director_simulator.database.models import DeviceTag
from fog_director_simulator.database.models import EnergyConsumptionType
from fog_director_simulator.database.models import Job
from fog_director_simulator.database.models import JobDeviceAllocation
from fog_director_simulator.database.models import JobIntensivity
from fog_director_simulator.database.models import JobMetric
from fog_director_simulator.database.models import JobMetricType
from fog_director_simulator.database.models import JobSampling
from fog_director_simulator.database.models import JobStatus
from fog_director_simulator.database.models import MyApp
from fog_director_simulator.database.models import MyAppMetric
from fog_director_simulator.database.models import MyAppMetricType


@pytest.fixture
def database_config() -> Config:
    return Config(
        drivername='sqlite',
        host=None,
        database_name=None,
        username=None,
        password=None,
        port=None,
    )


@pytest.fixture
def database(database_config):
    return DatabaseClient(
        config=database_config,
        verbose=False,
    )


@pytest.fixture
def verbose_database(database_config):
    return DatabaseClient(
        config=database_config,
        verbose=True,
    )


@pytest.fixture
def iterationCount() -> int:
    return 42


@pytest.fixture
def application() -> Application:
    return Application(
        localAppId='localAppId',
        version='1',
        name='name',
        description='description',
        isPublished=False,
        profileNeeded=ApplicationProfile.Small,
    )


@pytest.fixture
def device() -> Device:
    return Device(
        deviceId='deviceId',
        port=1,
        ipAddress='ipAddress',
        username='username',
        password='password',
        timeOfCreation=1,
        isAlive=True,
        reservedCPU=1.0,
        totalCPU=2,
        _cpuMetricsDistributionMean=3.0,
        _cpuMetricsDistributionStdDev=4.0,
        reservedMEM=5.0,
        totalMEM=6,
        _memMetricsDistributionMean=7.0,
        _memMetricsDistributionStdDev=8.0,
        chaosDieProb=9.0,  # Column(Float)
        chaosReviveProb=10.0,
        energyConsumptionType=EnergyConsumptionType.LARGE,
    )


@pytest.fixture
def my_app(application: Application, ) -> MyApp:
    return MyApp(
        myAppId=42,
        application=application,
        name='name',
        creationTime=42,
    )


@pytest.fixture
def device_tag(device: Device) -> DeviceTag:
    return DeviceTag(
        device=device,
        tag='tag',
    )


@pytest.fixture
def job(my_app: MyApp) -> Job:
    return Job(
        myApp=my_app,
        status=JobStatus.DEPLOY,
        profile=JobIntensivity.NORMAL,
    )


@pytest.fixture
def job_device_allocation(device: Device, job: Job) -> JobDeviceAllocation:
    return JobDeviceAllocation(
        device=device,
        job=job,
        profile='profile',  # TODO shouldn't this be a ApplicationProfile
    )


@pytest.fixture
def device_metric(device: Device, iterationCount: int) -> DeviceMetric:
    return DeviceMetric(
        iterationCount=iterationCount,
        device=device,
        metricType=DeviceMetricType.CPU,
        value=1.0,
    )


@pytest.fixture
def job_metric(job: Job, iterationCount: int) -> JobMetric:
    return JobMetric(
        iterationCount=iterationCount,
        job=job,
        metricType=JobMetricType.UP_STATUS,
        value=1.0,
    )


@pytest.fixture
def my_app_metric(my_app: MyApp, iterationCount: int) -> MyAppMetric:
    return MyAppMetric(
        iterationCount=iterationCount,
        myApp=my_app,
        metricType=MyAppMetricType.UP_STATUS,
        value=1.0,
    )


@pytest.fixture
def device_sampling(device: Device, iterationCount: int) -> DeviceSampling:
    return DeviceSampling(
        device=device,
        iterationCount=iterationCount,
        criticalCpuPercentage=1.0,
        criticalMemPercentage=2.0,
        averageCpuUsed=3.0,
        averageMemUsed=4.0,
        averageMyAppCount=5.0,
    )


@pytest.fixture
def job_sampling(job: Job, iterationCount: int) -> JobSampling:
    return JobSampling(
        job=job,
        iterationCount=iterationCount,
    )
