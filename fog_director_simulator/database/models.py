import enum
from typing import Any
from typing import cast
from typing import Dict
from typing import NamedTuple

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import composite
from sqlalchemy.orm import configure_mappers
from sqlalchemy.orm import relationship


class SQLORMDictMixin:
    def to_dict(self) -> Dict[str, Any]:
        """Convert this model into a dictionary."""
        # Note: this approach is a best effort approach and not meant to be the most performing one
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns  # type: ignore
        }

    def __repr__(self) -> str:
        return '<{type_name}: {primary_keys}>'.format(
            type_name=type(self).__name__,
            primary_keys=', '.join(
                f'{column.name}={getattr(self, column.name)}'
                for column in self.__table__.primary_key.columns  # type: ignore
            ),
        )


Base = declarative_base(cls=(SQLORMDictMixin, object,))


def create_all_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)


def prune_all_tables(engine: Engine) -> None:
    # TODO: instead of drop and create use DELETE
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


# Application Related objects
class ApplicationProfile(enum.Enum):
    Tiny = 0
    Small = 1
    Medium = 2
    Large = 3
    XLarge = 4
    Custom = 5

    def iox_name(self) -> str:
        return _APPLICATION_PROFILE_TO_IOX_NAME_MAPPING[self]

    @classmethod
    def from_iox_name(cls, iox_name: str) -> 'ApplicationProfile':
        return _IOX_NAME_TO_APPLICATION_PROFILE_IOX_MAPPING[iox_name]


_APPLICATION_PROFILE_TO_IOX_NAME_MAPPING = {
    ApplicationProfile.Tiny: 'c1.tiny',
    ApplicationProfile.Small: 'c1.small',
    ApplicationProfile.Medium: 'c1.medium',
    ApplicationProfile.Large: 'c1.large',
    ApplicationProfile.XLarge: 'c1.xlarge',
    ApplicationProfile.Custom: 'custom',
}
_IOX_NAME_TO_APPLICATION_PROFILE_IOX_MAPPING = {
    v: k
    for k, v in _APPLICATION_PROFILE_TO_IOX_NAME_MAPPING.items()
}


class Application(Base):  # type: ignore
    __tablename__ = 'applications'

    localAppId = Column(String(255), primary_key=True)
    version = Column(String(255), primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    isPublished = Column(Boolean)
    profileNeeded = cast(ApplicationProfile, Column(Enum(ApplicationProfile)))
    _cpuUsage = Column(Float, nullable=True)
    _memoryUsage = Column(Float, nullable=True)
    # TODO: should we have references?
    myApps = relationship('MyApp', back_populates='application')

    @property
    def cpuUsage(self) -> float:
        if self.profileNeeded == ApplicationProfile.Tiny:
            return 100
        elif self.profileNeeded == ApplicationProfile.Small:
            return 200
        elif self.profileNeeded == ApplicationProfile.Medium:
            return 400
        elif self.profileNeeded == ApplicationProfile.Large:
            return 600
        elif self.profileNeeded == ApplicationProfile.XLarge:
            return 1200
        elif self._cpuUsage is not None:
            return self._cpuUsage
        else:
            raise RuntimeError('This should not be possible')

    @property
    def memoryUsage(self) -> float:
        if self.profileNeeded == ApplicationProfile.Tiny:
            return 32
        elif self.profileNeeded == ApplicationProfile.Small:
            return 64
        elif self.profileNeeded == ApplicationProfile.Medium:
            return 128
        elif self.profileNeeded == ApplicationProfile.Large:
            return 256
        elif self.profileNeeded == ApplicationProfile.XLarge:
            return 512
        elif self._memoryUsage is not None:
            return self._memoryUsage
        else:
            raise RuntimeError('This should not be possible')


# MyApp Related objects
class MyApp(Base):  # type: ignore
    __tablename__ = 'my_apps'
    __table_args__ = (
        ForeignKeyConstraint(  # type: ignore
            ('applicationLocalAppId', 'applicationVersion'),
            (Application.localAppId, Application.version),
        ),
    )

    myAppId = Column(Integer, primary_key=True, autoincrement=True)
    applicationLocalAppId = Column(String(255), nullable=False)  # Foreign keys for composite keys need to be defined in __table_args__
    applicationVersion = Column(String(255), nullable=False)  # Foreign keys for composite keys need to be defined in __table_args__
    application = relationship('Application', back_populates='myApps')
    name = Column(String(255), unique=True, nullable=False)
    minJobReplicas = Column(Integer, nullable=True)
    creationTime = Column(Integer)
    destructionTime = Column(Integer, nullable=True)
    jobs = relationship('Job', back_populates='myApp')


# Device Related objects
class EnergyConsumptionType(enum.Enum):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2


class Distribution(NamedTuple):
    mean: float
    std_deviation: float


class Device(Base):  # type: ignore
    __tablename__ = 'devices'

    # Fields provided by public interface
    deviceId = Column(String(255), primary_key=True)
    ipAddress = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    port = Column(String(255), default='8443')

    # Fields added for internal use
    timeOfCreation = Column(Integer, nullable=True)
    timeOfRemoval = Column(Integer, nullable=True)
    isAlive = Column(Boolean, default=True)
    reservedCPU = Column(Float, default=0, nullable=False)
    totalCPU = Column(Integer, nullable=False)
    _cpuMetricsDistributionMean = Column(Float, nullable=False)
    _cpuMetricsDistributionStdDev = Column(Float, nullable=False)
    cpuMetricsDistribution = composite(Distribution, _cpuMetricsDistributionMean, _cpuMetricsDistributionStdDev)
    reservedMEM = Column(Float, default=0)
    totalMEM = Column(Integer, nullable=False)
    _memMetricsDistributionMean = Column(Float, nullable=False)
    _memMetricsDistributionStdDev = Column(Float, nullable=False)
    memMetricsDistribution = composite(Distribution, _memMetricsDistributionMean, _memMetricsDistributionStdDev)
    chaosDieProb = Column(Float, nullable=False)
    chaosReviveProb = Column(Float, nullable=False)
    tags = relationship('DeviceTag', back_populates='device')
    energyConsumptionType = cast(EnergyConsumptionType, Column(Enum(EnergyConsumptionType), default=EnergyConsumptionType.MEDIUM))

    @property
    def isInFogDirector(self) -> bool:
        return self.timeOfCreation is not None


class DeviceTag(Base):  # type: ignore  # TODO: we might nuke this
    __tablename__ = 'device_tags'

    deviceId = Column(String(255), ForeignKey(f'{Device.__tablename__}.deviceId'), primary_key=True)
    device = relationship('Device', back_populates='tags')
    tag = Column(String(255), primary_key=True)


# Job Related object
class JobStatus(enum.Enum):
    DEPLOY = 0
    START = 1
    STOP = 2
    UNINSTALLED = 3


class JobIntensivity(enum.Enum):
    QUIET = 0
    NORMAL = 1
    HEAVY = 2


class Job(Base):  # type: ignore
    __tablename__ = 'jobs'

    jobId = Column(Integer, primary_key=True, autoincrement=True)
    myAppId = Column(Integer, ForeignKey(f'{MyApp.__tablename__}.myAppId'), nullable=False)
    myApp = relationship('MyApp')
    status = cast(JobStatus, Column(Enum(JobStatus)))
    profile = cast(JobIntensivity, Column(Enum(JobIntensivity)))
    job_device_allocations = relationship('JobDeviceAllocation', back_populates='job')


class JobDeviceAllocation(Base):  # type: ignore
    __tablename__ = 'job_device_allocations'
    __table_args__ = (
        UniqueConstraint('deviceId', 'jobId'),
    )

    jobDeviceAllocationId = Column(Integer, primary_key=True, autoincrement=True)
    deviceId = Column(String(255), ForeignKey(f'{Device.__tablename__}.deviceId'), nullable=False)
    device = relationship('Device')
    jobId = Column(Integer, ForeignKey(f'{Job.__tablename__}.jobId'), nullable=False)
    job = relationship('Job')
    profile = cast(ApplicationProfile, Column(Enum(ApplicationProfile)))
    cpu = Column(Integer, nullable=False)
    memory = Column(Integer, nullable=False)


# Measured metrics
class DeviceMetricType(enum.Enum):
    APPS = 0
    CPU = 1
    MEM = 2
    ENERGY = 3
    UP_STATUS = 4


class DeviceMetric(Base):  # type: ignore
    __tablename__ = 'device_metrics'
    __table_args__ = (
        UniqueConstraint('iterationCount', 'deviceId', 'metricType'),
    )

    iterationCount = Column(Integer, primary_key=True)
    deviceId = Column(String(255), ForeignKey(f'{Device.__tablename__}.deviceId'), primary_key=True)
    device = relationship('Device')
    metricType = cast(DeviceMetricType, Column(Enum(DeviceMetricType), primary_key=True))
    value = Column(Float, nullable=False)


class JobMetricType(enum.Enum):
    ENOUGH_CPU = 0
    ENOUGH_MEM = 1
    UP_STATUS = 2


class JobMetric(Base):  # type: ignore
    __tablename__ = 'job_metrics'
    __table_args__ = (
        UniqueConstraint('iterationCount', 'jobId', 'metricType'),
    )

    iterationCount = Column(Integer, primary_key=True)
    jobId = Column(Integer, ForeignKey(f'{Job.__tablename__}.jobId'), primary_key=True)
    job = relationship('Job')
    metricType = cast(JobMetricType, Column(Enum(JobMetricType), primary_key=True))
    value = Column(Float, nullable=False)


class MyAppMetricType(enum.Enum):
    UP_STATUS = 1


class MyAppMetric(Base):  # type: ignore
    __tablename__ = 'my_app_metrics'
    __table_args__ = (
        UniqueConstraint('iterationCount', 'myAppId', 'metricType'),
    )

    iterationCount = Column(Integer, primary_key=True)
    myAppId = Column(Integer, ForeignKey(f'{MyApp.__tablename__}.myAppId'), primary_key=True)
    myApp = relationship('MyApp')
    metricType = cast(MyAppMetricType, Column(Enum(MyAppMetricType)))
    value = Column(Float, nullable=False)


# Pre-aggregate results of simulation (for frontend usage)
class DeviceSampling(Base):  # type: ignore
    __tablename__ = 'device_samplings'

    iterationCount = Column(Integer, primary_key=True)
    deviceId = Column(String(255), ForeignKey(f'{Device.__tablename__}.deviceId'), primary_key=True)
    device = relationship('Device')

    criticalCpuPercentage = Column(Float)
    criticalMemPercentage = Column(Float)
    averageCpuUsed = Column(Float)
    averageMemUsed = Column(Float)
    averageMyAppCount = Column(Float)


# Alerts
class AlertType(enum.Enum):
    NO_ALERT = 'NO_ALERT'
    APP_HEALTH = 'APP_HEALTH'
    DEVICE_REACHABILITY = 'DEVICE_REACHABILITY'
    CPU_CRITICAL_CONSUMPTION = 'CPU_CRITICAL_CONSUMPTION'
    MEM_CRITICAL_CONSUMPTION = 'MEM_CRITICAL_CONSUMPTION'


class Alert(Base):  # type: ignore
    __tablename__ = 'alerts'
    __table_args__ = (
        UniqueConstraint('myAppId', 'deviceId', 'type', 'time'),
    )

    alertId = Column(Integer, primary_key=True, autoincrement=True)
    myAppId = Column(Integer, ForeignKey(f'{MyApp.__tablename__}.myAppId'))
    myApp = relationship('MyApp')
    deviceId = Column(String(255), ForeignKey(f'{Device.__tablename__}.deviceId'), nullable=False)
    device = relationship('Device')
    type = cast(AlertType, Column(Enum(AlertType)))
    time = Column(Integer, nullable=False)


class MyAppAlertStatistic(Base):  # type: ignore
    __tablename__ = 'my_app_alert_statistics'

    myAppId = Column(Integer, ForeignKey(f'{MyApp.__tablename__}.myAppId'), primary_key=True)
    myApp = relationship('MyApp')
    type = cast(AlertType, Column(Enum(AlertType), primary_key=True))
    count = Column(Integer, nullable=False)


class SimulationInformation(Base):  # type: ignore
    __tablename__ = 'simulation_information'

    # TODO: this is ugly, but it a dumb and easy way to share a flag between processes (not the fastest one for sure)
    _id = Column(Integer, primary_key=True, autoincrement=True)
    simulationTime = Column(Integer, nullable=False)


configure_mappers()  # Force inter-table relations setup
