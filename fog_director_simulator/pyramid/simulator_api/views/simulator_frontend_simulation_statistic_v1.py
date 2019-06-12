from sys import maxsize

from pyramid.request import Request
from pyramid.view import view_config
from sqlalchemy import func

from fog_director_simulator.database.models import DeviceMetric
from fog_director_simulator.database.models import DeviceMetricType
from fog_director_simulator.database.models import MyAppMetric
from fog_director_simulator.database.models import MyAppMetricType
from fog_director_simulator.pyramid.simulator_api.formatters import simulator_statistics_format
from fog_director_simulator.pyramid.simulator_api.formatters import SimulatorStatisticsApi


@view_config(route_name='api.simulator_frontend.simulation_statistic.v1', request_method='GET')
def get_simulator_statistics(request: Request) -> SimulatorStatisticsApi:
    totalNumberOfSamplings = request.swagger_data['totalNumberOfSamplings']
    minIterationCount = request.swagger_data['minIterationCount'] or 0
    maxIterationCount = min(request.simulation_time, request.swagger_data['maxIterationCount'] or maxsize)

    up_status_statistics = request.database_logic.get_my_app_metric_statistics(
        stat_value=func.avg(MyAppMetric.value),
        metricType=MyAppMetricType.UP_STATUS,
        minIterationCount=minIterationCount,
        maxIterationCount=maxIterationCount,
    )

    total_energy_consumption = request.database_logic.get_device_metric_statistics(
        stat_value=func.sum(DeviceMetric.value),
        metricType=DeviceMetricType.ENERGY,
        minIterationCount=minIterationCount,
        maxIterationCount=maxIterationCount,
    )

    alert_statistics = request.database_logic.evaluate_custom_alert_statistics(
        simulationTime=request.simulation_time,
    )

    number_of_running_apps = len(request.database_logic.get_all_my_apps())

    return simulator_statistics_format(
        totalNumberOfSamplings=totalNumberOfSamplings,
        minIterationCount=minIterationCount,
        maxIterationCount=maxIterationCount,
        up_status_statistics=up_status_statistics,
        total_energy_consumption=total_energy_consumption,
        alert_statistics=alert_statistics,
        number_of_running_apps=number_of_running_apps,
    )
