import typing

if typing.TYPE_CHECKING:
    from webtest import TestApp


def test_post_simulator_add_device_description_v1_without_params(testapp: 'TestApp') -> None:
    response = testapp.post('/api/simulator_management/device/v1', expect_errors=True)
    assert response.status_code == 400


def test_post_simulator_add_device_description_v1_with_params(testapp: 'TestApp') -> None:
    response = testapp.post_json(
        '/api/simulator_management/device/v1',
        params={
            "deviceId": 1,
            'ipAddress': '1.1.1.1',
            'username': 'user',
            'password': 'pass',
            'port': 5656,
            'totalCPU': 100,
            'cpuMetricsDistributionMean': 80,
            'cpuMetricsDistributionStdDev': 20,
            'totalMEM': 512,
            'memMetricsDistributionMean': 400,
            'memMetricsDistributionStdDev': 50,
            'chaosDieProb': 1,
            'chaosReviveProb': 0,
        }
    )
    assert response.status_code == 201
