from webtest import TestApp


def test_post_v1_appmgr_myapps_my_app_id_action_without_tokens(testapp):
    # type: (TestApp) -> None
    response = testapp.post('/api/v1/appmgr/myapps/{my_app_id}/action', expect_errors=True)
    assert response.status_code == 400
