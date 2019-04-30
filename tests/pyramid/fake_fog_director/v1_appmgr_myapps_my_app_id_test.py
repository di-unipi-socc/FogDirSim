from webtest import TestApp


def test_delete_v1_appmgr_myapps_my_app_id_without_tokens(testapp):
    # type: (TestApp) -> None
    response = testapp.delete('/api/v1/appmgr/myapps/{my_app_id}', expect_errors=True)
    assert response.status_code == 400
