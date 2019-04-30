from webtest import TestApp


def test_get_v1_appmgr_localapps_without_tokens(testapp):
    # type: (TestApp) -> None
    response = testapp.get('/api/v1/appmgr/localapps', expect_errors=True)
    assert response.status_code == 400
