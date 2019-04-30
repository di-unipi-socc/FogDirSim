from webtest import TestApp


def test_put_v1_appmgr_localapps_local_application_id_version_without_tokens(testapp):
    # type: (TestApp) -> None
    response = testapp.put('/api/v1/appmgr/localapps/{local_application_id}:{version}', expect_errors=True)
    assert response.status_code == 400
