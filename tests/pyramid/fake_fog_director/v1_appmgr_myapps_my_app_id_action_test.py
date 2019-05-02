from unittest import mock

from webtest import TestApp

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import ApplicationProfile
from fog_director_simulator.database.models import Device
from fog_director_simulator.database.models import Job
from fog_director_simulator.database.models import JobStatus
from fog_director_simulator.database.models import MyApp


def test_post_v1_appmgr_myapps_my_app_id_action_without_tokens(testapp: TestApp) -> None:
    response = testapp.post('/api/v1/appmgr/myapps/{my_app_id}/action', expect_errors=True)
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_deploy_without_my_app(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
    my_app_id = my_app.myAppId
    device_id = device.deviceId

    database_logic.create(device)

    response = testapp.post_json(
        f'/api/v1/appmgr/myapps/{my_app_id}/action',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params={
            'deploy': {
                'devices': [
                    {
                        'deviceId': device_id,
                        'resourceAsk': {
                            'resources': {
                                'cpu': 0,
                                'memory': 0,
                                'profile': ApplicationProfile.Tiny.iox_name(),
                            },
                        },
                    },
                ],
            },
        },
    )
    assert response.status_code == 404


def test_post_v1_appmgr_myapps_my_app_id_action_deploy_with_unpublished_my_app(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
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
        params={
            'deploy': {
                'devices': [
                    {
                        'deviceId': device_id,
                        'resourceAsk': {
                            'resources': {
                                'cpu': 0,
                                'memory': 0,
                                'profile': ApplicationProfile.Tiny.iox_name(),
                            },
                        },
                    },
                ],
            },
        },
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_deploy_with_dead_device(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
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
        params={
            'deploy': {
                'devices': [
                    {
                        'deviceId': device_id,
                        'resourceAsk': {
                            'resources': {
                                'cpu': 0,
                                'memory': 0,
                                'profile': ApplicationProfile.Tiny.iox_name(),
                            },
                        },
                    },
                ],
            },
        },
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_deploy_with_not_enough_cpu(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
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
        params={
            'deploy': {
                'devices': [
                    {
                        'deviceId': device_id,
                        'resourceAsk': {
                            'resources': {
                                'cpu': 2,
                                'memory': 0,
                                'profile': ApplicationProfile.Tiny.iox_name(),
                            },
                        },
                    },
                ],
            },
        },
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_deploy_with_not_enough_mem(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
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
        params={
            'deploy': {
                'devices': [
                    {
                        'deviceId': device_id,
                        'resourceAsk': {
                            'resources': {
                                'cpu': 0,
                                'memory': 2,
                                'profile': ApplicationProfile.Tiny.iox_name(),
                            },
                        },
                    },
                ],
            },
        },
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_deploy_with_success(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
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
        params={
            'deploy': {
                'devices': [
                    {
                        'deviceId': device_id,
                        'resourceAsk': {
                            'resources': {
                                'cpu': 1,
                                'memory': 1,
                                'profile': ApplicationProfile.Tiny.iox_name(),
                            },
                        },
                    },
                ],
            },
        },
    )
    assert response.status_code == 200
    assert response.json == {
        'jobId': mock.ANY,
    }


def test_post_v1_appmgr_myapps_my_app_id_action_start_with_no_jobs(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
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
        params={'start': {}},
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_start_with_a_stopped_job(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device, job: Job) -> None:
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
        params={'start': {}},
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_start_with_success(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device, job: Job) -> None:
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
        params={'start': {}},
    )
    assert response.status_code == 200
    assert response.json == {
        'jobId': mock.ANY,
    }


def test_post_v1_appmgr_myapps_my_app_id_action_stop_with_no_jobs(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device) -> None:
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
        params={'stop': {}},
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_stop_with_a_stopped_job(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device, job: Job) -> None:
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
        params={'stop': {}},
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_my_app_id_action_stop_with_success(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device, job: Job) -> None:
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
        params={'stop': {}},
    )
    assert response.status_code == 200
    assert response.json == {
        'jobId': mock.ANY,
    }


def test_post_v1_appmgr_myapps_my_app_id_action_undeploy_with_a_undeployped_job(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device, job: Job) -> None:
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
        params={'undeploy': {'devices': [device_id]}},
    )
    assert response.status_code == 200
    assert response.json == {
        'jobId': mock.ANY,
    }


def test_post_v1_appmgr_myapps_my_app_id_action_undeploy_with_success(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, device: Device, job: Job) -> None:
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
        params={'undeploy': {'devices': [device_id]}},
    )
    assert response.status_code == 200
    assert response.json == {
        'jobId': mock.ANY,
    }
