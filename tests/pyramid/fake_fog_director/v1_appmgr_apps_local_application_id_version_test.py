from webtest import TestApp

from fog_director_simulator.database import Application
from fog_director_simulator.database import DatabaseLogic


def test_delete_v1_appmgr_apps_local_application_id_version_without_token(testapp: TestApp) -> None:
    response = testapp.delete('/api/v1/appmgr/apps/local_app:1', expect_errors=True)
    assert response.status_code == 400


def test_delete_v1_appmgr_apps_local_application_id_version_no_application(testapp: TestApp) -> None:
    response = testapp.delete(
        '/api/v1/appmgr/apps/local_app:1',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.status_code == 200


def test_delete_v1_appmgr_apps_local_application_id_version_with_application(testapp: TestApp, database_logic: DatabaseLogic, application: Application) -> None:
    local_app_id = application.localAppId
    version = application.version
    database_logic.create(application)
    response = testapp.delete(
        f'/api/v1/appmgr/apps/{local_app_id}:{version}',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.status_code == 200
