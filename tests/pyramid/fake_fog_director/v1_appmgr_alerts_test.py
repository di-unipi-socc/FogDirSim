import typing

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import Alert
from fog_director_simulator.pyramid.fake_fog_director.formatters import AlertApi
if typing.TYPE_CHECKING:
    from webtest import TestApp


def test_get_v1_appmgr_alerts_without_token(testapp: 'TestApp') -> None:
    response = testapp.get('/api/v1/appmgr/alerts', expect_errors=True)
    assert response.status_code == 400


def test_get_v1_appmgr_alerts_no_alerts(testapp: 'TestApp') -> None:
    response = testapp.get(
        '/api/v1/appmgr/alerts',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.json == {'data': []}


def test_get_v1_appmgr_alerts_with_alerts(testapp: 'TestApp', database_logic: DatabaseLogic, alert: Alert, formatted_alert: AlertApi) -> None:
    database_logic.create(alert)
    response = testapp.get(
        '/api/v1/appmgr/alerts',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.json == {'data': [formatted_alert]}
