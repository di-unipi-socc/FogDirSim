from unittest import mock

from webtest import TestApp

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import Application
from fog_director_simulator.database.models import MyApp


def test_post_v1_appmgr_myapps_without_tokens(testapp: TestApp) -> None:
    response = testapp.post('/api/v1/appmgr/myapps', expect_errors=True)
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_with_invalid_application_parameters(testapp, database_logic, application):
    # type: (TestApp, DatabaseLogic, Application) -> None
    params = {
        'name': 'my_app_name',
        'sourceAppName': f'{application.localAppId}:{application.version}:aaa',
        'version': application.version,
    }

    database_logic.create(application)
    response = testapp.post_json(
        '/api/v1/appmgr/myapps',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params=params,
    )
    assert response.status_code == 400


def test_post_v1_appmgr_myapps_with_already_created_name(testapp: TestApp, database_logic: DatabaseLogic, application: Application, my_app: MyApp) -> None:
    params = {
        'name': my_app.name,
        'sourceAppName': f'{application.localAppId}:{application.version}',
        'version': application.version,
    }
    database_logic.create(application, my_app)
    response = testapp.post_json(
        '/api/v1/appmgr/myapps',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
        params=params,
    )
    assert response.status_code == 409


def test_post_v1_appmgr_myapps_with_valid_application_parameters(testapp: TestApp, database_logic: DatabaseLogic, application: Application) -> None:
    params = {
        'name': 'new_app_name',
        'sourceAppName': f'{application.localAppId}:{application.version}',
        'version': application.version,
    }
    database_logic.create(application)
    response = testapp.post_json(
        '/api/v1/appmgr/myapps',
        headers={
            'X-Token-Id': 'token',
        },
        params=params,
    )
    assert response.status_code == 200
    assert response.json == {
        'myAppId': mock.ANY,
        'name': 'new_app_name',
    }


def test_get_v1_appmgr_myapps_without_tokens(testapp: TestApp) -> None:
    response = testapp.get('/api/v1/appmgr/myapps', expect_errors=True)
    assert response.status_code == 400
