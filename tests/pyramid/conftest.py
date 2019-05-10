import typing
from itertools import count
from unittest import mock

import pytest

from fog_director_simulator.database import Config
from fog_director_simulator.database import DatabaseClient
from fog_director_simulator.database import DatabaseLogic


@pytest.fixture
def mock_database_client(database_config: Config) -> typing.Generator[DatabaseClient, None, None]:
    with mock.patch('fog_director_simulator.pyramid.database.DatabaseClient', autospec=True) as m:
        m.return_value = DatabaseClient(database_config)
        yield m.return_value


@pytest.fixture
def database_logic(mock_database_client: DatabaseClient) -> typing.Generator[DatabaseLogic, None, None]:
    with mock.patch.object(mock_database_client.logic, 'get_simulation_time', autospec=True) as mock_get_simulation_time:
        mock_get_simulation_time.side_effect = count()
        yield mock_database_client.logic
        mock_get_simulation_time.side_effect = count()
