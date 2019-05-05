from mypy_extensions import TypedDict


class DeviceDescription(TypedDict):
    deviceId: str
    ipAddress: str
    port: str
    username: str
    password: str
    totalCPU: int
    cpuMetricsDistributionMean: float
    cpuMetricsDistributionStdDev: float
    totalMEM: int
    memMetricsDistributionMean: float
    memMetricsDistributionStdDev: float
    chaosDieProb: float
    chaosReviveProb: float
