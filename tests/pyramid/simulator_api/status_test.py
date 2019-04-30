from webtest import TestApp

from fog_director_simulator.pyramid import SIMULATION_TIME_END_HEADER
from fog_director_simulator.pyramid import SIMULATION_TIME_START_HEADER


def test_status(testapp):
    # type: (TestApp) -> None
    response = testapp.get('/api/status')
    assert response.json == {}
    assert response.headers[SIMULATION_TIME_START_HEADER] == '0'
    assert response.headers[SIMULATION_TIME_END_HEADER] == '1'
