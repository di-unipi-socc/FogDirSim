import pytest
from webtest import TestApp


@pytest.mark.xfail
def test_get_simulator_frontend_iteration_count_v1_without_tokens(testapp):
    # type: (TestApp) -> None
    response = testapp.get('/api/simulator_frontend/iteration_count/v1', expect_errors=True)
    assert response.status_code == 400
