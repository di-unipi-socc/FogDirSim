import typing
from itertools import count
from unittest import mock

import pytest

from fog_director_simulator.database import Config
from fog_director_simulator.database import DatabaseClient
from fog_director_simulator.database import DatabaseLogic


@pytest.fixture
def database_logic(database_config: Config) -> typing.Generator[DatabaseLogic, None, None]:
    with mock.patch('fog_director_simulator.pyramid._database_logic', autospec=True) as mock__database_logic:
        mock__database_logic.return_value = DatabaseClient(database_config).logic
        with mock.patch.object(mock__database_logic.return_value, 'get_simulation_time', autospec=True) as mock_get_simulation_time:
            mock_get_simulation_time.side_effect = count()
            yield mock__database_logic.return_value
            mock_get_simulation_time.side_effect = count()
