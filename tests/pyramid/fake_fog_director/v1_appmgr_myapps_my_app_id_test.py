from webtest import TestApp

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.database.models import MyApp
from fog_director_simulator.pyramid.fake_fog_director.formatters import MyAppApi


def test_delete_v1_appmgr_myapps_my_app_id_without_tokens(testapp: TestApp) -> None:
    response = testapp.delete('/api/v1/appmgr/myapps/{my_app_id}', expect_errors=True)
    assert response.status_code == 400


def test_delete_v1_appmgr_myapps_my_app_id_without_my_app(testapp: TestApp) -> None:
    response = testapp.delete(
        '/api/v1/appmgr/myapps/0',
        expect_errors=True,
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.status_code == 404


def test_delete_v1_appmgr_myapps_my_app_id_with_my_app(testapp: TestApp, database_logic: DatabaseLogic, my_app: MyApp, formatted_my_app: MyAppApi) -> None:
    my_app_id = my_app.myAppId
    database_logic.create(my_app)

    response = testapp.delete(
        f'/api/v1/appmgr/myapps/{my_app_id}',
        headers={
            'X-Token-Id': 'token',
        },
    )
    assert response.status_code == 200
    assert response.json == formatted_my_app
