from webtest import TestApp


def test_post_v1_appmgr_myapps_without_tokens(testapp):
    # type: (TestApp) -> None
    response = testapp.post('/api/v1/appmgr/myapps', expect_errors=True)
    assert response.status_code == 400


def test_get_v1_appmgr_myapps_without_tokens(testapp):
    # type: (TestApp) -> None
    response = testapp.get('/api/v1/appmgr/myapps', expect_errors=True)
    assert response.status_code == 400
