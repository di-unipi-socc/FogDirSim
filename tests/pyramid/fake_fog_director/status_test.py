import typing

from fog_director_simulator.pyramid import SIMULATION_TIME_END_HEADER
from fog_director_simulator.pyramid import SIMULATION_TIME_START_HEADER
if typing.TYPE_CHECKING:
    from webtest import TestApp


def test_get_status(testapp_not_increasing_time: 'TestApp') -> None:
    response = testapp_not_increasing_time.get('/api/status')
    assert response.json == {}
    assert response.headers[SIMULATION_TIME_START_HEADER] == '0'
    assert response.headers[SIMULATION_TIME_END_HEADER] == '0'


def test_get_status_slow(testapp: 'TestApp') -> None:
    response = testapp.get('/api/status_slow')
    assert response.json == {}
    assert response.headers[SIMULATION_TIME_START_HEADER] == '0'
    assert response.headers[SIMULATION_TIME_END_HEADER] == '2'
