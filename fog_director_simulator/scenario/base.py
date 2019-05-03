from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Optional
from typing import TypeVar

from bravado.client import SwaggerClient

from fog_director_simulator.database.models import Device
from fog_director_simulator.scenario.context import api_context
from fog_director_simulator.scenario.context import fog_director_context
from fog_director_simulator.scenario.context import simulator_context
from fog_director_simulator.scenario.database_utils import ScenarioDatabaseUtilMixin


T = TypeVar('T', bound='BaseScenario')


class BaseScenario(ABC, ScenarioDatabaseUtilMixin):
    """
    This class has a lot of code-duplication ... we should clean it up to make it presentable and more importantly usable
    """
    fog_director_username = 'username'
    fog_director_password = 'password'
    scenario_devices: List[Device] = []
    api_client: Optional[SwaggerClient]
    fog_director_client: SwaggerClient
    iteration_count = 0

    def __init__(
        self,
        max_simulation_iterations: Optional[int] = None,
        fog_director_api_url: Optional[str] = None,
    ):
        self.is_alive = True
        self.max_simulation_iterations = max_simulation_iterations
        self.scenario_devices_in_fog_director = self.scenario_devices
        self.fog_director_api_url = fog_director_api_url  # if None then the simulated fog_director is used

    def create_devices(self) -> None:
        """
        Add devices to DB
        """
        if self.api_client is None:
            return
        self.api_client.simulator_management.post_devices_v1(
            body={'devices': self.scenario_devices},
        ).result()

    @abstractmethod
    def configure_infrastructure(self) -> None:
        """
        Add devices or myapps or whatever via Fog Director APIs
        """
        pass

    @abstractmethod
    def manage_iteration(self) -> None:
        """
        React to alerts and stuff
        """
        pass

    def run(self) -> None:
        with api_context(self.fog_director_api_url) as self.api_client, \
                fog_director_context(self.fog_director_api_url) as self.fog_director_client:

            self.create_devices()

            with simulator_context():
                self.configure_infrastructure()
                while (
                    self.is_alive and
                    (
                        self.max_simulation_iterations is None or
                        self.iteration_count <= self.max_simulation_iterations
                    )
                ):
                    self.manage_iteration()
