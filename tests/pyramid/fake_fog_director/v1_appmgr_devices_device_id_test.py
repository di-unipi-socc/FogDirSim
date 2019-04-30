from webtest import TestApp


def test_delete_v1_appmgr_devices_device_id_without_tokens(testapp):
    # type: (TestApp) -> None
    response = testapp.delete('/api/v1/appmgr/devices/{device_id}', expect_errors=True)
    assert response.status_code == 400
