from typing import Any
from typing import Dict

from webtest import TestApp

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import Application


def test_get_v1_appmgr_localapps_without_tokens(testapp):
    # type: (TestApp) -> None
    response = testapp.get('/api/v1/appmgr/localapps', expect_errors=True)
    assert response.status_code == 400


def test_get_v1_appmgr_localapps_no_application(testapp):
    # type: (TestApp) -> None
    response = testapp.get(
        '/api/v1/appmgr/localapps',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.status_code == 200
    assert response.json == {'data': []}


def test_get_v1_appmgr_localapps_with_applications(testapp, database_logic, application, formatted_application):
    # type: (TestApp, DatabaseLogic, Application, Dict[str, Any]) -> None
    database_logic.create(application)
    response = testapp.get(
        '/api/v1/appmgr/localapps',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.status_code == 200
    assert response.json == {'data': [formatted_application]}
