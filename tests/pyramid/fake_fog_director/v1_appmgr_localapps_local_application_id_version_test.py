from typing import Any
from typing import Dict

from webtest import TestApp

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import Application


def test_put_v1_appmgr_localapps_local_application_id_version_without_tokens(testapp):
    # type: (TestApp) -> None
    response = testapp.put('/api/v1/appmgr/localapps/{local_application_id}:{version}', expect_errors=True)
    assert response.status_code == 400


def test_put_v1_appmgr_localapps_local_application_id_version_without_application(testapp):
    # type: (TestApp) -> None
    response = testapp.put_json(
        '/api/v1/appmgr/localapps/local_application_id:version',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },

        params={
            'creationDate': 0,
            'localAppId': 'local_application_id',
            'version': 'version',
            'published': 'published',
            'profileNeeded': 'c1.tiny',
            'cpuUsage': 0,
            'memoryUsage': 0,
            'sourceAppName': 'local_application_id:version'
        },

    )
    assert response.status_code == 404


def test_put_v1_appmgr_localapps_local_application_id_version_with_application(testapp, database_logic, application, formatted_application):
    # type: (TestApp, DatabaseLogic, Application, Dict[str, Any]) -> None

    params = {
        'creationDate': 0,
        'localAppId': application.localAppId,
        'version': application.version,
        'published': 'unpublished' if application.isPublished else 'published',
        'profileNeeded': application.profileNeeded.iox_name(),
        'cpuUsage': 0,
        'memoryUsage': 0,
        'sourceAppName': f'{application.localAppId}:{application.version}',
    }
    database_logic.create(application)
    response = testapp.put_json(
        f'/api/v1/appmgr/localapps/{params["localAppId"]}:{params["version"]}',
        headers={
            'X-Token-Id': 'token',
        },
        params=params,
    )
    assert response.status_code == 200
    assert response.json == dict(
        formatted_application,
        published='published',
    )
