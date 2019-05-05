from pyramid.httpexceptions import HTTPCreated
from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.database import Device


@view_config(route_name='api.simulator_management.device.v1', request_method='POST')
def post_simulator_management_device_v1(request: Request) -> None:
    body = request.swagger_data['body']
    request.database_logic.create(
        Device(
            deviceId=body['deviceId'],
            ipAddress=body['ipAddress'],
            username=body['username'],
            password=body['password'],
            port=body['port'],
            isAlive=True,
            totalCPU=body['totalCPU'],
            _cpuMetricsDistributionMean=body['cpuMetricsDistributionMean'],
            _cpuMetricsDistributionStdDev=body['cpuMetricsDistributionStdDev'],
            totalMEM=body['totalMEM'],
            _memMetricsDistributionMean=body['memMetricsDistributionMean'],
            _memMetricsDistributionStdDev=body['memMetricsDistributionStdDev'],
            chaosDieProb=body['chaosDieProb'],
            chaosReviveProb=body['chaosReviveProb'],
        )
    )

    raise HTTPCreated()
