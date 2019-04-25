from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import DeviceMetricType
from fog_director_simulator.database.models import EnergyConsumptionType


METRIC_TYPE = DeviceMetricType.ENERGY


def large_device(cpu_usage: float, mem_usage: float) -> float:
    if cpu_usage < 425:
        return 7
    elif cpu_usage < 850:
        return 12
    elif cpu_usage < 1275:
        return 20
    else:
        return 30


def medium_device(cpu_usage: float, mem_usage: float) -> float:
    if cpu_usage < 425:
        return 6
    elif cpu_usage < 850:
        return 10
    elif cpu_usage < 1275:
        return 20
    else:
        return 25


def small_device(cpu_usage: float, mem_usage: float) -> float:
    if cpu_usage < 425:
        return 5
    elif cpu_usage < 850:
        return 10
    elif cpu_usage < 1275:
        return 18
    else:
        return 25


_ENERGY_CONSUMPTION = {
    EnergyConsumptionType.SMALL: small_device,
    EnergyConsumptionType.MEDIUM: medium_device,
    EnergyConsumptionType.LARGE: large_device,
}


def collect(db_logic: DatabaseLogic, device_id: str) -> float:
    device = db_logic.get_device(device_id=device_id)
    cpu_usage = db_logic.get_device_metric(device_id=device_id, metric_type=DeviceMetricType.CPU).value
    mem_usage = db_logic.get_device_metric(device_id=device_id, metric_type=DeviceMetricType.MEM).value

    if cpu_usage is None or mem_usage is None:
        raise RuntimeError('This should not happen as this metric should be computed only after CPU and MEM collection')

    return _ENERGY_CONSUMPTION[device.energy_consumption_type](cpu_usage, mem_usage)
