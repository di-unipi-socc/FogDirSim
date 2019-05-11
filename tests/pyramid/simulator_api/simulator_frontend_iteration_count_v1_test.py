import typing
from itertools import count

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.pyramid.simulator_api.formatters import IterationCountApi

if typing.TYPE_CHECKING:
    from webtest import TestApp


def test_get_simulator_frontend_iteration_count_v1(testapp: 'TestApp', database_logic: DatabaseLogic) -> None:
    database_logic.get_simulation_time.side_effect = count(start=10)  # type: ignore

    response = testapp.get('/api/simulator_frontend/iteration_count/v1', expect_errors=False)
    assert response.status_code == 200
    assert response.json == IterationCountApi(iteration_count=10)
