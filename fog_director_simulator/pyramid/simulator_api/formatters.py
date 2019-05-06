from typing import List
from typing import Mapping

from mypy_extensions import TypedDict

from fog_director_simulator.database.models import AlertType


class AlertApi(TypedDict):
    NoAlert: float
    AppHealth: float
    DeviceReachability: float
    CpuUsage: float
    MemUsage: float


class SimulatorStatisticsApi(TypedDict):
    totalNumberOfSamplings: int
    minIterationCount: int
    maxIterationCount: int
    averageUptime: List[float]
    totalEnergyConsumption: List[float]
    alerts: AlertApi


def alert_format(
    alert_statistics: Mapping[AlertType, float],
) -> AlertApi:
    return AlertApi(
        NoAlert=alert_statistics.get(AlertType.NO_ALERT, 0),
        AppHealth=alert_statistics.get(AlertType.APP_HEALTH, 0),
        DeviceReachability=alert_statistics.get(AlertType.DEVICE_REACHABILITY, 0),
        CpuUsage=alert_statistics.get(AlertType.CPU_CRITICAL_CONSUMPTION, 0),
        MemUsage=alert_statistics.get(AlertType.MEM_CRITICAL_CONSUMPTION, 0),
    )


def simulator_statistics_format(
    totalNumberOfSamplings: int,
    minIterationCount: int,
    maxIterationCount: int,
    up_status_statistics: Mapping[int, float],
    total_energy_consumption: Mapping[int, float],
    alert_statistics: Mapping[AlertType, float],
) -> SimulatorStatisticsApi:
    # TODO: we do not care of totalNumberOfSamplings for now
    return SimulatorStatisticsApi(
        totalNumberOfSamplings=totalNumberOfSamplings,
        minIterationCount=minIterationCount,
        maxIterationCount=maxIterationCount,
        averageUptime=[value for value in up_status_statistics.values()],
        totalEnergyConsumption=[value for value in total_energy_consumption.values()],
        alerts=alert_format(alert_statistics),
    )


class IterationCountApi(TypedDict):
    iteration_count: int


def iteration_count_format(iteration_count: int) -> IterationCountApi:
    return IterationCountApi(iteration_count=iteration_count)
