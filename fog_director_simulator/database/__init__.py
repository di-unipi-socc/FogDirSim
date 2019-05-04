import os
from itertools import groupby
from sys import maxsize
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Tuple

from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from fog_director_simulator.database.models import Alert
from fog_director_simulator.database.models import AlertType
from fog_director_simulator.database.models import Application
from fog_director_simulator.database.models import Base
from fog_director_simulator.database.models import create_all_tables
from fog_director_simulator.database.models import Device
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
from fog_director_simulator.database.models import prune_all_tables


class Config(NamedTuple):
    drivername: str = 'mysql+mysqldb'
    username: Optional[str] = 'root'
    password: Optional[str] = 'password'
    host: Optional[str] = 'database'
    port: Optional[int] = 3306
    database_name: Optional[str] = 'fog_director'
    verbose: bool = False

    @classmethod
    def from_environment(cls) -> 'Config':
        return cls(
            drivername=os.environ.get('DB_DRIVERNAME', Config._field_defaults['drivername']),
            username=os.environ.get('DB_USERNAME', Config._field_defaults['username']),
            password=os.environ.get('DB_PASSWORD', Config._field_defaults['password']),
            host=os.environ.get('DB_HOST', Config._field_defaults['host']),
            port=int(os.environ.get('DB_PORT', Config._field_defaults['port'])),
            database_name=os.environ.get('DB_DATABASE_NAME', Config._field_defaults['database_name']),
            verbose=os.environ.get('DB_VERBOSE', str(Config._field_defaults['verbose'])) == str(True),
        )

    def to_environment_dict(self) -> Dict[str, str]:
        return {
            'DB_DRIVERNAME': self.drivername,
            'DB_USERNAME': self.username or '',
            'DB_PASSWORD': self.password or '',
            'DB_HOST': self.host or '',
            'DB_PORT': str(self.port if self.port is not None else ''),
            'DB_DATABASE_NAME': self.database_name or '',
            'DB_VERBOSE': str(self.verbose),
        }


class DatabaseClient:
    def __init__(self, config: Config) -> None:
        self._engine = create_engine(
            URL(
                drivername=config.drivername,
                username=config.username,
                password=config.password,
                host=config.host,
                port=config.port,
                database=config.database_name,
            ),
            echo=config.verbose,
        )
        create_all_tables(self._engine)
        self._SessionClass = sessionmaker(bind=self._engine)
        self._session = None
        self.logic = DatabaseLogic(self)

    def reset_database(self) -> None:
        prune_all_tables(self._engine)

    def __enter__(self) -> Session:
        if self._session is None:
            self._session = self._SessionClass()
        self._session.begin_nested()  # type: ignore
        return self._session  # type: ignore

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        assert self._session  # type guard for type checking to ensure that `self._session is not None`
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

        return False


class DatabaseLogic:
    def __init__(self, database_client: DatabaseClient):
        self._client = database_client

    def __enter__(self) -> Session:
        return self._client.__enter__()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        return self._client.__exit__(exc_type, exc_val, exc_tb)

    def create(self, *sql_alchemy_mapping: Base) -> Tuple[Base, ...]:
        with self as session:
            session.add_all(sql_alchemy_mapping)
            session.flush(sql_alchemy_mapping)
            return sql_alchemy_mapping

    def delete(self, *sql_alchemy_mapping: Base) -> None:
        with self as session:
            for instance in sql_alchemy_mapping:
                session.delete(instance)

    def get_device(self, deviceId: str) -> Device:
        with self as session:
            device = session.query(Device).get(deviceId)
            if device is None:
                raise NoResultFound()
            return device

    def get_device_metric(self, iterationCount: int, deviceId: str, metricType: DeviceMetricType) -> DeviceMetric:
        with self as session:
            device_metric = session.query(DeviceMetric).get({
                'iterationCount': iterationCount,
                'deviceId': deviceId,
                'metricType': metricType,
            })
            if device_metric is None:
                raise NoResultFound()
            return device_metric

    def get_job(self, jobId: int) -> Job:
        with self as session:
            job = session.query(Job).get(jobId)
            if job is None:
                raise NoResultFound()
            return job

    def get_job_metric(self, iterationCount: int, jobId: int, metricType: JobMetricType) -> JobMetric:
        with self as session:
            job_metric = session.query(JobMetric).get({
                'iterationCount': iterationCount,
                'jobId': jobId,
                'metricType': metricType,
            })
            if job_metric is None:
                raise NoResultFound()
            return job_metric

    def get_application(self, localAppId: str, version: str) -> Application:
        with self as session:
            application = session.query(Application).get({
                'localAppId': localAppId,
                'version': version,
            })
            if application is None:
                raise NoResultFound()
            return application

    def get_my_app(self, myAppId: int) -> MyApp:
        with self as session:
            my_app = session.query(MyApp).get(myAppId)
            if my_app is None:
                raise NoResultFound()
            return my_app

    def get_all_devices(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        currently_on_the_infrastructure: bool = True,
    ) -> Iterable[Device]:
        with self as session:
            query = session.query(Device)
            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)

            if currently_on_the_infrastructure:
                query = query.filter(Device.timeOfRemoval is None)

            return query.all()

    def get_all_jobs(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        jobStatus: Optional[Iterable[JobStatus]] = None,
        myAppId: Optional[int] = None,
    ) -> Iterable[Job]:
        with self as session:
            query = session.query(Job)
            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)

            if jobStatus is None:
                query = query.filter(Job.status != JobStatus.UNINSTALLED)
            elif not jobStatus:
                return []  # Let's avoid to issue the query as we already know the result
            else:
                query = query.filter(Job.status.in_(jobStatus))  # type: ignore

            if myAppId is not None:
                query = query.filter(Job.myAppId == myAppId)

            return query.all()

    def get_all_my_apps(self, limit: Optional[int] = None, offset: Optional[int] = None) -> Iterable[MyApp]:
        with self as session:
            query = session.query(
                MyApp,
            )
            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)

            return query.all()

    def get_device_metrics(self, deviceId: str, metricType: DeviceMetricType) -> Iterable[DeviceMetric]:
        with self as session:
            query = session.query(DeviceMetric).filter(
                DeviceMetric.deviceId == deviceId,
                DeviceMetric.metricType == metricType,
            )

            return query.all()

    def get_device_metric_statistics(
        self,
        metricType: DeviceMetric,
        stat_value: Any,  # TODO: give better type
        minIterationCount: Optional[int] = None,
        maxIterationCount: Optional[int] = None,
    ) -> Mapping[int, float]:
        with self as session:
            query = session.query(
                DeviceMetric.iterationCount,
                stat_value,
            ).filter(
                DeviceMetric.metricType == metricType,
            )
            if minIterationCount is not None:
                query = query.filter(
                    DeviceMetric.iterationCount >= minIterationCount,
                )
            if maxIterationCount is not None:
                query = query.filter(
                    DeviceMetric.iterationCount <= maxIterationCount,
                )

            query = query.group_by(
                DeviceMetric.iterationCount,
            )

            return {
                iteration_count: stat_value
                for (iteration_count, stat_value) in query
            }

    def get_my_app_metric_statistics(
        self,
        metricType: MyAppMetricType,
        stat_value: Any,  # TODO: give better type
        minIterationCount: Optional[int] = None,
        maxIterationCount: Optional[int] = None,
    ) -> Mapping[int, float]:
        with self as session:
            query = session.query(
                MyAppMetric.iterationCount,
                stat_value,
            ).filter(
                MyAppMetric.metricType == metricType,
            )
            if minIterationCount is not None:
                query = query.filter(
                    MyAppMetric.iterationCount >= minIterationCount,
                )
            if maxIterationCount is not None:
                query = query.filter(
                    MyAppMetric.iterationCount <= maxIterationCount,
                )

            query = query.group_by(
                MyAppMetric.iterationCount,
            )

            return {
                iteration_count: stat_value
                for (iteration_count, stat_value) in query
            }

    def get_my_app_alert_statistics(self, myApp: MyApp, alert_type: AlertType) -> Optional[MyAppAlertStatistic]:
        with self as session:
            query = session.query(MyAppAlertStatistic).filter(
                MyAppAlertStatistic.myApp == myApp,
                MyAppAlertStatistic.type == alert_type,
            )

            return query.one_or_none()

    def get_alerts(self, iterationCount: int) -> Iterable[MyAppAlertStatistic]:
        with self as session:
            query = session.query(Alert).filter(
                Alert.time == iterationCount,
            )

            return query.all()

    def get_simulation_time(self) -> int:
        with self as session:
            return session.query(func.max(DeviceSampling.iterationCount)).scalar() or 0

    def delete_application(self, localAppId: str, version: int) -> None:
        with self as session:
            session.query(
                Application,
            ).filter(
                Application.localAppId == localAppId,
                Application.version == version,
            ).delete()

    def get_device_from_arguments(self, port: str, ipAddress: str, username: str, password: str) -> Device:
        with self as session:
            query = session.query(
                Device,
            ).filter(
                Device.port == port,
                Device.ipAddress == ipAddress,
                Device.username == username,
                Device.password == password,
            )

            return query.one()

    def get_devices(self, limit: Optional[int] = None, offset: Optional[int] = None) -> Iterable[Device]:
        with self as session:
            query = session.query(
                Device,
            )
            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)

            return query.all()

    def get_applications(self, limit: Optional[int] = None, offset: Optional[int] = None) -> Iterable[Application]:
        with self as session:
            query = session.query(
                Application,
            )
            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)

            return query.all()

    def get_application_by_name(self, name: str) -> Optional[Application]:
        with self as session:
            query = session.query(
                Application,
            ).filter(
                Application.name == name,
            )

            return query.first()

    def get_my_app_by_name(self, name: str) -> Optional[MyApp]:
        with self as session:
            query = session.query(
                MyApp,
            ).filter(
                MyApp.name == name,
            )

            return query.first()

    def evaluate_custom_alert_statistics(self, simulationTime: int) -> Mapping[AlertType, float]:
        with self as session:
            # TODO: maybe optimize to do it in db only
            query = session.query(MyAppAlertStatistic).order_by(
                MyAppAlertStatistic.type,
            )
            result = {}
            for alert_type, statistics in groupby(query, lambda my_app_alert_statistic: my_app_alert_statistic.type):
                total_count, total_lifetime = 0, 0
                for my_app_alert_statistic in statistics:
                    my_app_lifetime = (
                        min(
                            simulationTime,
                            my_app_alert_statistic.myApp.destructionTime or maxsize,
                        ) -
                        my_app_alert_statistic.myApp.creationTime
                    )
                    total_count += my_app_alert_statistic.count
                    total_lifetime += my_app_lifetime
                result[alert_type] = total_count / total_lifetime

            return result
