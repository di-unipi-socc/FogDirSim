import typing

from fog_director_simulator.database.models import Device

if typing.TYPE_CHECKING:
    from webtest import TestApp


def test_post_simulator_add_device_description_v1_without_params(testapp: 'TestApp') -> None:
    response = testapp.post('/api/simulator_management/device/v1', expect_errors=True)
    assert response.status_code == 400


def test_post_simulator_add_device_description_v1_with_params(testapp: 'TestApp', device: Device) -> None:
    response = testapp.post_json(
        '/api/simulator_management/device/v1',
        params={
            'deviceId': device.deviceId,
            'ipAddress': device.ipAddress,
            'username': device.username,
            'password': device.password,
            'port': device.port,
            'totalCPU': device.totalCPU,
            'cpuMetricsDistributionMean': device._cpuMetricsDistributionMean,
            'cpuMetricsDistributionStdDev': device._cpuMetricsDistributionStdDev,
            'totalMEM': device.totalMEM,
            'memMetricsDistributionMean': device._memMetricsDistributionMean,
            'memMetricsDistributionStdDev': device._memMetricsDistributionStdDev,
            'chaosDieProb': device.chaosDieProb,
            'chaosReviveProb': device.chaosReviveProb,
        },
    )
    assert response.status_code == 201
