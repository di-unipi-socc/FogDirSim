import os
from typing import Iterable
from typing import NamedTuple
from typing import Optional
from typing import Tuple

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from fog_director_simulator.database.models import AlertType
from fog_director_simulator.database.models import Application
from fog_director_simulator.database.models import Base
from fog_director_simulator.database.models import create_all_tables
from fog_director_simulator.database.models import Device
from fog_director_simulator.database.models import DeviceMetric
from fog_director_simulator.database.models import DeviceMetricType
from fog_director_simulator.database.models import Job
from fog_director_simulator.database.models import JobMetric
from fog_director_simulator.database.models import JobMetricType
from fog_director_simulator.database.models import JobStatus
from fog_director_simulator.database.models import MyApp
from fog_director_simulator.database.models import MyAppAlertStatistic
from fog_director_simulator.database.models import prune_all_tables


class Config(NamedTuple):
    drivername: str = 'mysql+mysqldb'
    username: Optional[str] = 'root'
    password: Optional[str] = 'password'
    host: Optional[str] = 'database'
    port: Optional[int] = 3306
    database_name: Optional[str] = 'fog_director'

    @staticmethod
    def from_environment() -> 'Config':
        return Config(
            drivername=os.environ.get('DB_DRIVERNAME', Config._field_defaults['drivername']),
            username=os.environ.get('DB_USERNAME', Config._field_defaults['username']),
            password=os.environ.get('DB_PASSWORD', Config._field_defaults['password']),
            host=os.environ.get('DB_HOST', Config._field_defaults['host']),
            port=int(os.environ.get('DB_PORT', Config._field_defaults['port'])),
            database_name=os.environ.get('DB_DATABASE_NAME', Config._field_defaults['database_name']),
        )


class DatabaseClient:
    def __init__(self, config: Config, verbose: bool = False) -> None:
        self._engine = create_engine(
            URL(
                drivername=config.drivername,
                username=config.username,
                password=config.password,
                host=config.host,
                port=config.port,
                database=config.database_name,
            ),
            echo=verbose,
        )
        create_all_tables(self._engine)
        self._SessionClass = sessionmaker(bind=self._engine)
        self._session = None
        self.logic = DatabaseLogic(self)

    def reset_database(self):
        prune_all_tables(self._engine)

    def __enter__(self):
        if self._session is None:
            self._session = self._SessionClass()
        self._session.begin_nested()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._session.rollback()
        else:
            self._session.commit()

        if not self._session.transaction.nested:
            if exc_type is not None:
                self._session.rollback()
            else:
                self._session.commit()
            self._session.close()


def with_session(func):
    def wrapper(self, *args, **kwargs):
        if args and isinstance(args[0], Session):
            return func(self, *args, **kwargs)
        else:
            with self._client as session:
                return func(self, session, *args, **kwargs)
    return wrapper


class DatabaseLogic:
    def __init__(self, database_client: DatabaseClient):
        self._client = database_client

    def __enter__(self):
        return self._client.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._client.__exit__(exc_type, exc_val, exc_tb)

    @with_session
    def create(self, session: Session, *sql_alchemy_mapping: Base) -> Tuple[Base, ...]:
        session.add_all(sql_alchemy_mapping)
        session.flush(sql_alchemy_mapping)
        return sql_alchemy_mapping

    @with_session
    def get_device(self, session: Session, deviceId: str) -> Optional[Device]:
        return session.query(Device).get(deviceId)

    @with_session
    def get_device_metric(self, session: Session, iterationCount: int, deviceId: str, metricType: DeviceMetricType) -> Optional[DeviceMetric]:
        return session.query(DeviceMetric).get({
            'iterationCount': iterationCount,
            'deviceId': deviceId,
            'metricType': metricType,
        })

    @with_session
    def get_job(self, session: Session, jobId: str) -> Optional[Job]:
        return session.query(Job).get(jobId)

    @with_session
    def get_job_metric(self, session: Session, iterationCount: int, jobId: str, metricType: JobMetricType) -> Optional[JobMetric]:
        return session.query(JobMetric).get({
            'iterationCount': iterationCount,
            'jobId': jobId,
            'metricType': metricType,
        })

    @with_session
    def get_application(self, session: Session, localAppId: str, version: int) -> Optional[Application]:
        return session.query(Application).get({
            'localAppId': localAppId,
            'version': version,
        })

    @with_session
    def get_my_app(self, session: Session, myAppId: str) -> Optional[MyApp]:
        return session.query(MyApp).get(myAppId)

    @with_session
    def get_all_devices(self, session: Session, currently_on_the_infrastructure: bool = True) -> Iterable[Device]:
        query = session.query(Device)
        if currently_on_the_infrastructure:
            query = query.filter(Device.timeOfRemoval is None)
        return query.all()

    @with_session
    def get_all_jobs(self, session: Session, jobStatus: Optional[Iterable[JobStatus]] = None, myAppId: Optional[str] = None) -> Iterable[Job]:
        query = session.query(Job)
        if jobStatus is None:
            query = query.filter(Job.status != JobStatus.UNINSTALLED)
        elif not jobStatus:
            return []  # Let's avoid to issue the query as we already know the result
        else:
            query = query.filter(Job.status.in_(jobStatus))

        if myAppId is not None:
            query = query.filter(Job.myAppId == myAppId)

        return query.all()

    @with_session
    def get_device_metrics(
        self,
        session: Session,
        deviceId: str,
        metricType: DeviceMetricType,
    ) -> Iterable[DeviceMetric]:
        query = session.query(DeviceMetric).filter(
            DeviceMetric.deviceId == deviceId,
            DeviceMetric.metricType == metricType,
        )

        return query.all()

    @with_session
    def get_my_app_alert_statistics(
        self,
        session: Session,
        myApp: MyApp,
        alert_type: AlertType,
    ) -> Optional[MyAppAlertStatistic]:
        query = session.query(MyAppAlertStatistic).filter(
            MyAppAlertStatistic.myApp == myApp,
            MyAppAlertStatistic.type == alert_type,
        )

        return query.one_or_none()
