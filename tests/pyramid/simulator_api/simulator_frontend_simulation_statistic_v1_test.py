import typing
from itertools import count
from unittest import mock

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import AlertType
from fog_director_simulator.database.models import Application
from fog_director_simulator.database.models import Device
from fog_director_simulator.database.models import DeviceMetric
from fog_director_simulator.database.models import DeviceMetricType
from fog_director_simulator.database.models import EnergyConsumptionType
from fog_director_simulator.database.models import MyApp
from fog_director_simulator.database.models import MyAppAlertStatistic
from fog_director_simulator.database.models import MyAppMetric
from fog_director_simulator.database.models import MyAppMetricType
if typing.TYPE_CHECKING:
    from webtest import TestApp


def test_get_simulator_frontend_simulation_statistic_v1_without_totalNumberOfSamplings(testapp: 'TestApp') -> None:
    response = testapp.get('/api/simulator_frontend/simulation_statistic/v1', expect_errors=True)
    assert response.status_code == 400


def test_get_simulator_frontend_simulation_statistic_v1_with_my_apps_if_no_data(
    testapp: 'TestApp',
    database_logic: DatabaseLogic,
    application: Application,
    my_app: MyApp,
) -> None:
    database_logic.get_simulation_time.side_effect = count(start=10)  # type: ignore
    response = testapp.get('/api/simulator_frontend/simulation_statistic/v1?totalNumberOfSamplings=2')
    assert response.status_code == 200
    assert response.json == {
        'totalNumberOfSamplings': 2,
        'minIterationCount': 0,
        'maxIterationCount': 10,
        'averageUptime': [],
        'totalEnergyConsumption': [],
        'alerts': {
            'AppHealth': 0,
            'CpuUsage': 0,
            'DeviceReachability': 0,
            'MemUsage': 0,
            'NoAlert': 0,
        },
    }


def test_get_simulator_frontend_simulation_statistic_v1_with_my_apps_validate_upstatus(
    testapp: 'TestApp',
    database_logic: DatabaseLogic,
    application: Application,
    my_app: MyApp,
) -> None:
    database_logic.get_simulation_time.side_effect = count(start=10)  # type: ignore

    database_logic.create(
        MyAppMetric(  # type: ignore
            iterationCount=1,
            myApp=my_app,
            metricType=MyAppMetricType.UP_STATUS,
            value=True,
        ),
        MyAppMetric(  # type: ignore
            iterationCount=2,
            myApp=my_app,
            metricType=MyAppMetricType.UP_STATUS,
            value=False,
        ),
        MyAppMetric(  # type: ignore
            iterationCount=2,
            myApp=MyApp(
                myAppId=1,
                application=application,
                name='test-name',
                creationTime=42,
            ),
            metricType=MyAppMetricType.UP_STATUS,
            value=True,
        )
    )

    response = testapp.get('/api/simulator_frontend/simulation_statistic/v1?totalNumberOfSamplings=2')
    assert response.status_code == 200
    assert response.json == {
        'totalNumberOfSamplings': 2,
        'minIterationCount': 0,
        'maxIterationCount': 10,
        'averageUptime': [1, 0.5],
        'totalEnergyConsumption': mock.ANY,
        'alerts': mock.ANY,
    }


def test_get_simulator_frontend_simulation_statistic_v1_with_my_apps_validate_energy_consumption(
    testapp: 'TestApp',
    database_logic: DatabaseLogic,
    device: Device,
) -> None:
    database_logic.get_simulation_time.side_effect = count(start=10)  # type: ignore

    database_logic.create(
        DeviceMetric(  # type: ignore
            iterationCount=1,
            device=device,
            metricType=DeviceMetricType.ENERGY,
            value=0,
        ),
        DeviceMetric(  # type: ignore
            iterationCount=2,
            device=device,
            metricType=DeviceMetricType.ENERGY,
            value=1,
        ),
        DeviceMetric(  # type: ignore
            iterationCount=2,
            device=Device(  # type: ignore
                deviceId='test-deviceId',
                port='1',
                ipAddress='ipAddress',
                username='username',
                password='password',
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
            ),
            metricType=DeviceMetricType.ENERGY,
            value=1,
        ),
    )

    response = testapp.get('/api/simulator_frontend/simulation_statistic/v1?totalNumberOfSamplings=2')
    assert response.status_code == 200
    assert response.json == {
        'totalNumberOfSamplings': 2,
        'minIterationCount': 0,
        'maxIterationCount': 10,
        'averageUptime': mock.ANY,
        'totalEnergyConsumption': [0, 2],
        'alerts': mock.ANY,
    }


def test_get_simulator_frontend_simulation_statistic_v1_with_my_apps_validate_alert_statistics(
    testapp: 'TestApp',
    database_logic: DatabaseLogic,
    application: Application,
    my_app: MyApp,
) -> None:
    database_logic.get_simulation_time.side_effect = count(start=10)  # type: ignore

    database_logic.create(
        MyAppAlertStatistic(  # type: ignore
            myApp=my_app,
            type=AlertType.APP_HEALTH,
            count=2,
        ),
        MyAppAlertStatistic(  # type: ignore
            myApp=MyApp(
                myAppId=1,
                application=application,
                name='test-name-1',
                creationTime=0,
                destructionTime=2,
            ),
            type=AlertType.APP_HEALTH,
            count=2,
        ),
        MyAppAlertStatistic(  # type: ignore
            myApp=MyApp(
                myAppId=2,
                application=application,
                name='test-name-2',
                creationTime=6,
            ),
            type=AlertType.NO_ALERT,
            count=2,
        ),
    )

    response = testapp.get('/api/simulator_frontend/simulation_statistic/v1?totalNumberOfSamplings=2')
    assert response.status_code == 200
    assert response.json == {
        'totalNumberOfSamplings': 2,
        'minIterationCount': 0,
        'maxIterationCount': 10,
        'averageUptime': mock.ANY,
        'totalEnergyConsumption': mock.ANY,
        'alerts': {
            'AppHealth': 1 / 3,
            'CpuUsage': 0,
            'DeviceReachability': 0,
            'MemUsage': 0,
            'NoAlert': 0.5,
        },
    }
