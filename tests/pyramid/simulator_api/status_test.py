import typing

from fog_director_simulator.pyramid import SIMULATION_TIME_END_HEADER
from fog_director_simulator.pyramid import SIMULATION_TIME_START_HEADER
if typing.TYPE_CHECKING:
    from webtest import TestApp


def test_status(testapp: 'TestApp') -> None:
    response = testapp.get('/api/status')
    assert response.json == {}
    assert response.headers[SIMULATION_TIME_START_HEADER] == '0'
    assert response.headers[SIMULATION_TIME_END_HEADER] == '1'
