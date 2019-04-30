import pytest
from webtest import TestApp


@pytest.mark.xfail
def test_get_v1_appmgr_tokenservice_without_tokens(testapp):
    # type: (TestApp) -> None
    response = testapp.get('/api/v1/appmgr/tokenservice', expect_errors=True)
    assert response.status_code == 400
