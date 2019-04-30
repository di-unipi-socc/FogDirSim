from webtest import TestApp


def test_post_v1_appmgr_localapps_upload_without_tokens(testapp):
    # type: (TestApp) -> None
    response = testapp.post('/api/v1/appmgr/localapps/upload', expect_errors=True)
    assert response.status_code == 400
