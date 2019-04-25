import enum
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
    def to_dict(self):
        """Convert this model into a dictionary."""
        # Note: this approach is a best effort approach and not meant to be the most performing one
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self):
        return '<{type_name}: {primary_keys}>'.format(
            type_name=type(self).__name__,
            primary_keys=', '.join(
                f'{column.name}={getattr(self, column.name)}'
                for column in self.__table__.primary_key.columns
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


class Application(Base):  # type: ignore
    __tablename__ = 'applications'

    localAppId = Column(String(255), primary_key=True)
    version = Column(String(255), primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    isPublished = Column(Boolean)
    profileNeeded = Column(Enum(ApplicationProfile))
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
        ForeignKeyConstraint(
            ('applicationLocalAppId', 'applicationVersion'),
            (Application.localAppId, Application.version),
        ),
    )

    myAppId = Column(Integer, primary_key=True, autoincrement=True)
    applicationLocalAppId = Column(String(255))  # Foreign keys for composite keys need to be defined in __table_args__
    applicationVersion = Column(String(255))  # Foreign keys for composite keys need to be defined in __table_args__
    application = relationship('Application', back_populates='myApps')
    name = Column(String(255), unique=True)
    minJobReplicas = Column(Integer, nullable=True)
    creationTime = Column(Integer)
    destructionTime = Column(Integer, nullable=True)


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
    ipAddress = Column(String(255))
    username = Column(String(255))
    password = Column(String(255))
    port = Column(String, default='8443')

    # Fields added for internal use
    timeOfCreation = Column(Integer, nullable=True)
    timeOfRemoval = Column(Integer, nullable=True)
    isAlive = Column(Boolean, default=True)
    reservedCPU = Column(Float, default=0)
    totalCPU = Column(Integer)
    _cpuMetricsDistributionMean = Column(Float)
    _cpuMetricsDistributionStdDev = Column(Float)
    cpuMetricsDistribution = composite(Distribution, _cpuMetricsDistributionMean, _cpuMetricsDistributionStdDev)
    reservedMEM = Column(Float, default=0)
    totalMEM = Column(Integer)
    _memMetricsDistributionMean = Column(Float)
    _memMetricsDistributionStdDev = Column(Float)
    memMetricsDistribution = composite(Distribution, _memMetricsDistributionMean, _memMetricsDistributionStdDev)
    chaosDieProb = Column(Float)
    chaosReviveProb = Column(Float)
    tags = relationship('DeviceTag', back_populates='device')
    energyConsumptionType = Column(Enum(EnergyConsumptionType), default=EnergyConsumptionType.MEDIUM)

    @property
    def isInFogDirector(self):
        return self.timeOfCreation is not None


class DeviceTag(Base):  # type: ignore  # TODO: we might nuke this
    __tablename__ = 'device_tags'

    deviceId = Column(ForeignKey(f'{Device.__tablename__}.deviceId'), primary_key=True)
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
    myAppId = Column(ForeignKey(f'{MyApp.__tablename__}.myAppId'))
    myApp = relationship('MyApp')
    status = Column(Enum(JobStatus))
    profile = Column(Enum(JobIntensivity))
    devices = relationship('JobDeviceAllocation')  # TODO: is this safe???


class JobDeviceAllocation(Base):  # type: ignore
    __tablename__ = 'job_device_allocations'

    deviceId = Column(ForeignKey(f'{Device.__tablename__}.deviceId'), primary_key=True)
    device = relationship('Device')
    jobId = Column(ForeignKey(f'{Job.__tablename__}.jobId'), primary_key=True)
    job = relationship('Job')
    profile = Column(Enum(ApplicationProfile))
    cpu = Column(Integer)
    memory = Column(Integer)


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
    deviceId = Column(ForeignKey(f'{Device.__tablename__}.deviceId'), primary_key=True)
    device = relationship('Device')
    metricType = Column(Enum(DeviceMetricType), primary_key=True)
    value = Column(Float)


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
    jobId = Column(ForeignKey(f'{Job.__tablename__}.jobId'), primary_key=True)
    job = relationship('Job')
    metricType = Column(Enum(JobMetricType), primary_key=True)
    value = Column(Float)


class MyAppMetricType(enum.Enum):
    UP_STATUS = 1


class MyAppMetric(Base):  # type: ignore
    __tablename__ = 'my_app_metrics'
    __table_args__ = (
        UniqueConstraint('iterationCount', 'myAppId', 'metricType'),
    )

    iterationCount = Column(Integer, primary_key=True)
    myAppId = Column(ForeignKey(f'{MyApp.__tablename__}.myAppId'), primary_key=True)
    myApp = relationship('MyApp')
    metricType = Column(Enum(MyAppMetricType))
    value = Column(Float)


# Pre-aggregate results of simulation (for frontend usage)
class DeviceSampling(Base):  # type: ignore
    __tablename__ = 'device_samplings'

    iterationCount = Column(Integer, primary_key=True)
    deviceId = Column(ForeignKey(f'{Device.__tablename__}.deviceId'), primary_key=True)
    device = relationship('Device')

    criticalCpuPercentage = Column(Float)
    criticalMemPercentage = Column(Float)
    averageCpuUsed = Column(Float)
    averageMemUsed = Column(Float)
    averageMyAppCount = Column(Float)


# Alerts
class AlertType(enum.Enum):
    NO_ALERT = 0
    APP_HEALTH = 1
    DEVICE_REACHABILITY = 2
    CPU_CRITICAL_CONSUMPTION = 3
    MEM_CRITICAL_CONSUMPTION = 4


class Alert(Base):  # type: ignore
    __tablename__ = 'alerts'

    myAppId = Column(ForeignKey(f'{MyApp.__tablename__}.myAppId'), primary_key=True)
    myApp = relationship('MyApp')
    deviceId = Column(ForeignKey(f'{Device.__tablename__}.deviceId'), primary_key=True)
    device = relationship('Device')
    type = Column(Enum(AlertType), primary_key=True)
    time = Column(Integer, primary_key=True)


class MyAppAlertStatistic(Base):  # type: ignore
    __tablename__ = 'my_app_alert_statistics'

    myAppId = Column(ForeignKey(f'{MyApp.__tablename__}.myAppId'), primary_key=True)
    myApp = relationship('MyApp')
    type = Column(Enum(AlertType), primary_key=True)
    count = Column(Integer)


configure_mappers()  # Force inter-table relations setup
