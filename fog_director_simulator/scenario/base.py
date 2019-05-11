import json
import sys
from abc import ABC
from abc import abstractmethod
from argparse import ArgumentParser
from argparse import Namespace
from subprocess import Popen
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from bravado.client import SwaggerClient
from tqdm import tqdm

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
    api_process: Optional[Popen]
    database_config: Optional[Config]
    dump_file: Optional[str]
    fog_director_client: SwaggerClient
    fog_director_username = 'username'
    fog_director_password = 'password'
    fog_director_process: Optional[Popen]
    fog_director_token: str
    progress_bar: tqdm
    scenario_devices: List[Device] = []
    simulator_process: Optional[Popen]
    verbose_all: bool
    verbose_fog_director_api: bool
    verbose_simulator_api: bool
    verbose_simulator_engine: bool

    def __init__(
        self,
        dump_file: Optional[str],
        fog_director_api_url: Optional[str],
        max_simulation_iterations: Optional[int],
        verbose_all: bool,
        verbose_fog_director_api: bool,
        verbose_simulator_api: bool,
        verbose_simulator_engine: bool,
    ):
        assert fog_director_api_url is not None or max_simulation_iterations is not None
        self.dump_file = dump_file
        self.fog_director_api_url = fog_director_api_url  # if None then the simulated fog_director is used
        self.max_simulation_iterations = max_simulation_iterations
        self.scenario_devices_in_fog_director = self.scenario_devices
        self.verbose_all = verbose_all
        self.verbose_fog_director_api = verbose_fog_director_api
        self.verbose_simulator_api = verbose_simulator_api
        self.verbose_simulator_engine = verbose_simulator_engine

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
        mutuex_group = parser.add_mutually_exclusive_group(required=True)
        mutuex_group.add_argument(
            '--max-simulation-iterations',
            dest='max_simulation_iterations',
            type=int,
            help='Maximum number of iterations that will be simulated in the scenario (default %(default)s).',
        )
        mutuex_group.add_argument(
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
        parser.add_argument(
            '--verbose-all',
            dest='verbose_all',
            action='store_true',
            help='Enable all the verbose flags',
        )
        parser.add_argument(
            '--verbose-fog-director-api',
            dest='verbose_fog_director_api',
            action='store_true',
            help='Fog Director API logs (database and requests logs) are redirected to stderr',
        )
        parser.add_argument(
            '--verbose-simulator-api',
            dest='verbose_simulator_api',
            action='store_true',
            help='Simulator API logs (database and requests logs) are redirected to stderr',
        )
        parser.add_argument(
            '--verbose-simulator-engine',
            dest='verbose_simulator_engine',
            action='store_true',
            help='Simulator Engine logs (database logs) are redirected to stderr',
        )
        return parser

    @classmethod
    def _init_from_cli_args(cls, args: Namespace) -> 'BaseScenario':
        return cls(
            dump_file=args.dump_file,
            fog_director_api_url=args.fog_director_api_url,
            max_simulation_iterations=args.max_simulation_iterations,
            verbose_all=args.verbose_all,
            verbose_fog_director_api=args.verbose_fog_director_api,
            verbose_simulator_api=args.verbose_simulator_api,
            verbose_simulator_engine=args.verbose_simulator_engine,
        )

    def dump_statistics(self) -> None:
        if self.api_client is None:
            return

        statistics = self.simulation_statistics(number_of_samplings=200)
        statistics_string = json.dumps(statistics, sort_keys=True, indent=2)

        if self.verbose_all:
            print('Simulation Statistics')
            print(statistics_string)

        if self.dump_file is not None:
            with open(self.dump_file, 'w') as f:
                f.write(statistics_string)
        elif not self.verbose_all:
            print('Simulation Statistics')
            print(statistics_string)

    @classmethod
    def get_instance(cls: Type[T], argv: Optional[List[str]] = None) -> T:
        parser = cls._cli_parser()
        args = parser.parse_args(args=argv)
        if args.verbose_all:
            args.verbose_simulator_api = True
            args.verbose_fog_director_api = True
            args.verbose_simulator_engine = True
        instance = cls._init_from_cli_args(args)
        return instance  # type: ignore

    def _processes_alive(self) -> bool:
        if self.api_process is not None:
            return_code = self.api_process.poll()
            if return_code is not None:
                print(f'Simulator API terminated with status_code={return_code}')
                return False

        if self.fog_director_process is not None:
            return_code = self.fog_director_process.poll()
            if return_code is not None:
                print(f'Simulator API terminated with status_code={return_code}')
                return False

        if self.simulator_process is not None:
            return_code = self.simulator_process.poll()
            if return_code is not None:
                print(f'Simulator API terminated with status_code={return_code}')
                return False

        return True

    def run(self) -> None:
        with database_context(
            start_database=self.fog_director_api_url is None,
            verbose=self.verbose_all,
        ) as self.database_config, api_context(
            database_config=self.database_config,
            verbose=self.verbose_simulator_api,
        ) as (self.api_process, self.api_client), fog_director_context(
            database_config=self.database_config,
            fog_director_api_url=self.fog_director_api_url,
            verbose=self.verbose_fog_director_api,
        ) as (self.fog_director_process, self.fog_director_client), tqdm(
            total=self.max_simulation_iterations,
            desc=f'{self.__class__.__name__}',
            ascii=True,
        ) as self.progress_bar:
            self.fog_director_token = self.get_fog_director_token()

            self.create_devices()

            with simulator_context(
                database_config=self.database_config,
                max_simulation_iterations=self.max_simulation_iterations if self.max_simulation_iterations is not None else sys.maxsize - 1,
                verbose=self.verbose_simulator_engine,
            ) as self.simulator_process:
                self.configure_infrastructure()

                while True:
                    if not self._processes_alive():
                        break

                    iteration_count = None
                    if self.max_simulation_iterations is not None:
                        iteration_count = self.iteration_count()

                    if iteration_count and iteration_count >= self.max_simulation_iterations:  # type: ignore
                        break

                    self.progress_bar.n = iteration_count or 0
                    self.progress_bar.update(0)
                    self.manage_iteration()

            self.dump_statistics()
