import json
from abc import ABC
from abc import abstractmethod
from argparse import ArgumentParser
from argparse import Namespace
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from bravado.client import SwaggerClient

from fog_director_simulator.database import Config
from fog_director_simulator.database.models import Device
from fog_director_simulator.scenario.api_utils import ScenarioAPIUtilMixin
from fog_director_simulator.scenario.context import api_context
from fog_director_simulator.scenario.context import database_context
from fog_director_simulator.scenario.context import fog_director_context
from fog_director_simulator.scenario.context import simulator_context


T = TypeVar('T', bound='BaseScenario')


class BaseScenario(ABC, ScenarioAPIUtilMixin):
    """
    This class has a lot of code-duplication ... we should clean it up to make it presentable and more importantly usable
    """
    api_client: Optional[SwaggerClient]
    database_config: Optional[Config]
    fog_director_client: SwaggerClient
    fog_director_username = 'username'
    fog_director_password = 'password'
    fog_director_token: str
    scenario_devices: List[Device] = []
    verbose: bool
    dump_file: Optional[str]

    def __init__(
        self,
        dump_file: Optional[str],
        fog_director_api_url: Optional[str],
        max_simulation_iterations: Optional[int],
        verbose: bool,
    ):
        self.dump_file = dump_file
        self.fog_director_api_url = fog_director_api_url  # if None then the simulated fog_director is used
        self.is_alive = True
        self.max_simulation_iterations = max_simulation_iterations
        self.scenario_devices_in_fog_director = self.scenario_devices
        self.verbose = verbose

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

    @classmethod
    def _cli_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(description=cls.__doc__)
        parser.add_argument(
            '--verbose',
            dest='verbose',
            action='store_true',
            help='Run the scenario in verbose mode (all reporting and stdout/stderr '
                 'of all processes will be redirected to stderr)',
        )
        parser.add_argument(
            '--max-simulation-iterations',
            dest='max_simulation_iterations',
            type=int,
            help='Maximum number of iterations that will be simulated in the scenario. '
                 'NOTE: if the argument is not passed the simulation will never end',
        )
        parser.add_argument(
            '--fog-director-api-url',
            dest='fog_director_api_url',
            type=str,
            help='Run the scenario against a specific CISCO\'s Fog Director instance. '
                 'NOTE: if missing a complete emulated environment will be spawned.',
        )
        parser.add_argument(
            '--dump-file',
            dest='dump_file',
            type=str,
            help='File path where to save similation statistics. NOTE: If missing then stdout will be used.',
        )
        return parser

    @classmethod
    def _init_from_cli_args(cls, args: Namespace) -> 'BaseScenario':
        return cls(
            dump_file=args.dump_file,
            fog_director_api_url=args.fog_director_api_url,
            max_simulation_iterations=args.max_simulation_iterations,
            verbose=args.verbose,
        )

    def dump_statistics(self) -> None:
        if self.api_client is None:
            return

        statistics = self.api_client.get_simulator_frontend_simulation_statistic_v1(totalNumberOfSamplings=200).result()
        statistics_string = json.dumps(statistics, sort_keys=True, indent=2)

        if self.verbose:
            print('Simulation Statistics')
            print(statistics_string)

        if self.dump_file is not None:
            with open(self.dump_file, 'w') as f:
                f.write(statistics_string)
        elif not self.verbose:
            print('Simulation Statistics')
            print(statistics_string)

    @classmethod
    def get_instance(cls: Type[T], argv: Optional[List[str]] = None) -> T:
        parser = cls._cli_parser()
        instance = cls._init_from_cli_args(parser.parse_args(args=argv))
        return instance  # type: ignore

    def run(self) -> None:
        with database_context(
            start_database=self.fog_director_api_url is None,
            verbose=self.verbose,
        ) as self.database_config, api_context(
            database_config=self.database_config,
            verbose=self.verbose,
        ) as self.api_client, fog_director_context(
            database_config=self.database_config,
            fog_director_api_url=self.fog_director_api_url,
            verbose=self.verbose,
        ) as self.fog_director_client:
            self.fog_director_token = self.get_fog_director_token()

            self.create_devices()

            with simulator_context(self.database_config, self.verbose):
                self.configure_infrastructure()
                while (
                    self.is_alive and
                    (
                        self.max_simulation_iterations is None or
                        self.iteration_count() <= self.max_simulation_iterations
                    )
                ):
                    self.manage_iteration()

            self.dump_statistics()
