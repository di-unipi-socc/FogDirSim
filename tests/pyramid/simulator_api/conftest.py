import typing
from itertools import repeat
from unittest import mock

import pytest
from webtest import TestApp

from fog_director_simulator.database import DatabaseLogic
from fog_director_simulator.pyramid.simulator_api.webapp import create_application


@pytest.fixture
def testapp_not_increasing_time(database_logic: DatabaseLogic) -> typing.Generator[TestApp, None, None]:
    create_application.cache_clear()
    database_logic.get_simulation_time.side_effect = repeat(0)  # type: ignore  # the actual database logic is a mock ;)
    yield TestApp(app=create_application())


@pytest.fixture
def testapp(database_logic: DatabaseLogic) -> typing.Generator[TestApp, None, None]:
    create_application.cache_clear()
    with mock.patch('fog_director_simulator.pyramid.sleep', autospec=True):
        yield TestApp(app=create_application())
