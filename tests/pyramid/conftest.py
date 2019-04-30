import typing
from itertools import count
from itertools import repeat
from unittest import mock

import pytest
from webtest import TestApp

from fog_director_simulator.database import DatabaseClient
from fog_director_simulator.pyramid.fake_fog_director.webapp import create_application


@pytest.fixture
def database_logic(database_config):
    with mock.patch('fog_director_simulator.pyramid._database_logic', autospec=True) as mock__database_logic:
        mock__database_logic.return_value = DatabaseClient(database_config).logic
        with mock.patch.object(mock__database_logic.return_value, 'get_simulation_time', autospec=True) as mock_get_simulation_time:
            mock_get_simulation_time.side_effect = count()
            yield mock__database_logic.return_value
            mock_get_simulation_time.side_effect = count()


@pytest.fixture
def testapp_not_increasing_time(database_logic) -> typing.Generator[TestApp, None, None]:
    create_application.cache_clear()
    database_logic.get_simulation_time.side_effect = repeat(0)
    yield TestApp(app=create_application())


@pytest.fixture
def testapp(database_logic) -> typing.Generator[TestApp, None, None]:
    create_application.cache_clear()
    with mock.patch('fog_director_simulator.pyramid.sleep', autospec=True):
        yield TestApp(app=create_application())
