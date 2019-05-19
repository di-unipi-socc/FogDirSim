import typing
from unittest import mock

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import ApplicationProfile
from fog_director_simulator.database.models import Device
from fog_director_simulator.database.models import Job
from fog_director_simulator.database.models import JobStatus
from fog_director_simulator.database.models import MyApp
from fog_director_simulator.pyramid.fake_fog_director.request_types import ApplicationResourceAsk
from fog_director_simulator.pyramid.fake_fog_director.request_types import MyAppAction
from fog_director_simulator.pyramid.fake_fog_director.request_types import MyAppActionDeployDevices
from fog_director_simulator.pyramid.fake_fog_director.request_types import MyAppActionDeployItem
from fog_director_simulator.pyramid.fake_fog_director.request_types import MyAppActionUndeployDevices
from fog_director_simulator.pyramid.fake_fog_director.request_types import ResourceAsk

if typing.TYPE_CHECKING:
    from webtest import TestApp


def test_post_v1_appmgr_myapps_my_app_id_action_without_tokens(testapp: 'TestApp') -> None:
    response = testapp.post('/api/v1/appmgr/myapps/{my_app_id}/action', expect_errors=True)
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_deploy_without_my_app(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
    my_app_id = my_app.myAppId
    device_id = device.deviceId

    database_logic.create(device)

    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(
            deploy=MyAppActionDeployDevices(
                config={},
                metricsPollingFrequency='aaa',
                startApp=False,
                devices=[
                    MyAppActionDeployItem(
                        deviceId=device_id,
                        resourceAsk=ResourceAsk(
                            resources=ApplicationResourceAsk(
                                cpu=0,
                                memory=0,
                                profile=ApplicationProfile.Tiny.iox_name(),
                                network=[],
                            ),
                        ),
                    )
                ],
            ),
        ),
    )
    assert response.status_code == 404


def test_post_v1_appmgr_myapps_my_app_id_action_deploy_with_unpublished_my_app(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
    my_app_id = my_app.myAppId
    device_id = device.deviceId

    my_app.application.isPublished = False

    database_logic.create(my_app, device)
    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(
            deploy=MyAppActionDeployDevices(
                config={},
                metricsPollingFrequency='aaa',
                startApp=False,
                devices=[
                    MyAppActionDeployItem(
                        deviceId=device_id,
                        resourceAsk=ResourceAsk(
                            resources=ApplicationResourceAsk(
                                cpu=0,
                                memory=0,
                                profile=ApplicationProfile.Tiny.iox_name(),
                                network=[],
                            ),
                        ),
                    )
                ],
            ),
        ),
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_deploy_with_dead_device(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
    my_app_id = my_app.myAppId
    device_id = device.deviceId

    my_app.application.isPublished = True
    device.isAlive = False

    database_logic.create(my_app, device)
    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(
            deploy=MyAppActionDeployDevices(
                config={},
                metricsPollingFrequency='aaa',
                startApp=False,
                devices=[
                    MyAppActionDeployItem(
                        deviceId=device_id,
                        resourceAsk=ResourceAsk(
                            resources=ApplicationResourceAsk(
                                cpu=0,
                                memory=0,
                                profile=ApplicationProfile.Tiny.iox_name(),
                                network=[],
                            ),
                        ),
                    )
                ],
            ),
        ),
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_deploy_with_not_enough_cpu(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
    my_app_id = my_app.myAppId
    device_id = device.deviceId

    my_app.application.isPublished = True
    device.isAlive = True
    device.totalCPU = 10
    device.reservedCPU = 9

    database_logic.create(my_app, device)
    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(
            deploy=MyAppActionDeployDevices(
                config={},
                metricsPollingFrequency='aaa',
                startApp=False,
                devices=[
                    MyAppActionDeployItem(
                        deviceId=device_id,
                        resourceAsk=ResourceAsk(
                            resources=ApplicationResourceAsk(
                                cpu=2,
                                memory=0,
                                profile=ApplicationProfile.Tiny.iox_name(),
                                network=[],
                            ),
                        ),
                    )
                ],
            ),
        ),
    )
    assert response.status_code == 400
    with database_logic:
        assert database_logic.get_device(device_id).reservedCPU == 9


def test_post_v1_appmgr_myapps_my_app_id_action_deploy_with_not_enough_mem(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
    my_app_id = my_app.myAppId
    device_id = device.deviceId

    my_app.application.isPublished = True
    device.isAlive = True
    device.totalMEM = 10
    device.reservedMEM = 9

    database_logic.create(my_app, device)
    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(
            deploy=MyAppActionDeployDevices(
                config={},
                metricsPollingFrequency='aaa',
                startApp=False,
                devices=[
                    MyAppActionDeployItem(
                        deviceId=device_id,
                        resourceAsk=ResourceAsk(
                            resources=ApplicationResourceAsk(
                                cpu=0,
                                memory=2,
                                profile=ApplicationProfile.Tiny.iox_name(),
                                network=[],
                            ),
                        ),
                    )
                ],
            ),
        ),
    )
    assert response.status_code == 400
    with database_logic:
        assert database_logic.get_device(device_id).reservedMEM == 9


def test_post_v1_appmgr_myapps_my_app_id_action_deploy_with_success(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
    my_app_id = my_app.myAppId
    device_id = device.deviceId

    my_app.application.isPublished = True
    device.isAlive = True
    device.totalCPU = 10
    device.totalMEM = 10
    device.reservedCPU = 1
    device.reservedMEM = 1

    database_logic.create(my_app, device)
    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(
            deploy=MyAppActionDeployDevices(
                config={},
                metricsPollingFrequency='aaa',
                startApp=False,
                devices=[
                    MyAppActionDeployItem(
                        deviceId=device_id,
                        resourceAsk=ResourceAsk(
                            resources=ApplicationResourceAsk(
                                cpu=1,
                                memory=1,
                                profile=ApplicationProfile.Tiny.iox_name(),
                                network=[],
                            ),
                        ),
                    )
                ],
            ),
        ),
    )
    assert response.status_code == 200
    assert response.json == {
        'jobId': mock.ANY,
    }
    with database_logic:
        assert database_logic.get_device(device_id).reservedMEM == 2
        assert database_logic.get_device(device_id).reservedMEM == 2


def test_post_v1_appmgr_myapps_my_app_id_action_start_with_no_jobs(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
    my_app_id = my_app.myAppId

    my_app.application.isPublished = True
    device.isAlive = True
    device.totalCPU = 10
    device.totalMEM = 10
    device.reservedCPU = 1
    device.reservedMEM = 1

    database_logic.create(my_app, device)
    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(start={}),
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_start_with_a_stopped_job(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device, job: Job) -> None:
    my_app_id = my_app.myAppId

    my_app.application.isPublished = True
    device.isAlive = True
    device.totalCPU = 10
    device.totalMEM = 10
    device.reservedCPU = 1
    device.reservedMEM = 1
    job.status = JobStatus.STOP

    database_logic.create(job, my_app, device)
    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(start={}),
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_start_with_success(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device, job: Job) -> None:
    my_app_id = my_app.myAppId

    my_app.application.isPublished = True
    device.isAlive = True
    device.totalCPU = 10
    device.totalMEM = 10
    device.reservedCPU = 1
    device.reservedMEM = 1
    job.status = JobStatus.DEPLOY

    database_logic.create(job, my_app, device)
    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(start={}),
    )
    assert response.status_code == 200
    assert response.json == {
        'jobId': mock.ANY,
    }


def test_post_v1_appmgr_myapps_my_app_id_action_stop_with_no_jobs(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
    my_app_id = my_app.myAppId

    my_app.application.isPublished = True
    device.isAlive = True
    device.totalCPU = 10
    device.totalMEM = 10
    device.reservedCPU = 1
    device.reservedMEM = 1

    database_logic.create(my_app, device)
    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(stop={}),
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_stop_with_a_stopped_job(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device, job: Job) -> None:
    my_app_id = my_app.myAppId

    my_app.application.isPublished = True
    device.isAlive = True
    device.totalCPU = 10
    device.totalMEM = 10
    device.reservedCPU = 1
    device.reservedMEM = 1
    job.status = JobStatus.DEPLOY

    database_logic.create(job, my_app, device)
    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(stop={}),
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_stop_with_success(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device, job: Job) -> None:
    my_app_id = my_app.myAppId

    my_app.application.isPublished = True
    device.isAlive = True
    device.totalCPU = 10
    device.totalMEM = 10
    device.reservedCPU = 1
    device.reservedMEM = 1
    job.status = JobStatus.START

    database_logic.create(job, my_app, device)
    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(stop={}),
    )
    assert response.status_code == 200
    assert response.json == {
        'jobId': mock.ANY,
    }


def test_post_v1_appmgr_myapps_my_app_id_action_undeploy_with_a_undeployped_job(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device, job: Job) -> None:
    my_app_id = my_app.myAppId
    device_id = device.deviceId

    my_app.application.isPublished = True
    device.isAlive = True
    device.totalCPU = 10
    device.totalMEM = 10
    device.reservedCPU = 1
    device.reservedMEM = 1
    job.status = JobStatus.UNINSTALLED

    database_logic.create(job, my_app, device)
    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(undeploy=MyAppActionUndeployDevices(devices=[device_id])),
    )
    assert response.status_code == 200
    assert response.json == {
        'jobId': mock.ANY,
    }


def test_post_v1_appmgr_myapps_my_app_id_action_undeploy_with_success(testapp: 'TestApp', database_logic: DatabaseLogic, my_app: MyApp, device: Device, job: Job) -> None:
    my_app_id = my_app.myAppId
    device_id = device.deviceId

    my_app.application.isPublished = True
    device.isAlive = True
    device.totalCPU = 10
    device.totalMEM = 10
    device.reservedCPU = 1
    device.reservedMEM = 1
    job.status = JobStatus.START

    database_logic.create(job, my_app, device)
    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        headers={
            'X-Token-Id': 'token',
        },
        params=MyAppAction(undeploy=MyAppActionUndeployDevices(devices=[device_id])),
    )
    assert response.status_code == 200
    assert response.json == {
        'jobId': mock.ANY,
    }
