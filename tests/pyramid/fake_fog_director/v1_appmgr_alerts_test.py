from webtest import TestApp

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import Alert


def test_v1_appmgr_alerts_without_token(testapp):
    # type: (TestApp) -> None
    response = testapp.get('/api/v1/appmgr/alerts', expect_errors=True)
    assert response.status_code == 400


def test_v1_appmgr_alerts_no_alerts(testapp):
    # type: (TestApp) -> None
    response = testapp.get(
        '/api/v1/appmgr/alerts',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.json == {'data': []}


def test_v1_appmgr_alerts_with_alerts(testapp, database_logic, alert):
    # type: (TestApp, DatabaseLogic, Alert) -> None
    database_logic.create(alert)
    response = testapp.get(
        '/api/v1/appmgr/alerts',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.json == {
        'data': [
            {
                'deviceId': 'deviceId',
                'myAppId': 42,
                'time': 0,
                'type': 'APP_HEALTH',
            },
        ],
    }
