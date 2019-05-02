import typing

import pytest
if typing.TYPE_CHECKING:
    from webtest import TestApp


@pytest.mark.xfail
def test_get_simulator_frontend_simulation_statistic_v1_without_tokens(testapp: 'TestApp') -> None:
    response = testapp.get('/api/simulator_frontend/simulation_statistic/v1', expect_errors=True)
    assert response.status_code == 400
