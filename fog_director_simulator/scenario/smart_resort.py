from argparse import ArgumentParser
from argparse import ArgumentTypeError
from argparse import Namespace
from collections import defaultdict
from typing import Any
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from fog_director_simulator.database import Device
from fog_director_simulator.database import MyApp
from fog_director_simulator.database.models import AlertType
from fog_director_simulator.pyramid.fake_fog_director.formatters import ApplicationApi
from fog_director_simulator.scenario.base import BaseScenario


def positive_int(value: str) -> int:
    ivalue = int(value)
    if ivalue <= 0:
        raise ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def percentage(value: str) -> float:
    fvalue = float(value)
    if fvalue <= 0 or fvalue >= 1:
        raise ArgumentTypeError("%s is an invalid percentage (expected a value in [0,1])" % value)
    return fvalue


class SmartResort(BaseScenario):
    """
    This scenario simulates an arbitrary amount of room in a resort
    with an arbitrary amount of app in the resort. It tries to install
    all the application over the devices and then manages them.

    The devices are:
        5 BIG (2500 CPU, 1024 RAM, distr: 1700/500 CPU, 850/450 RAM)
        5 MEDIUM (1500 CPU, 1024 RAM, distr: 1000/400 CPU, 750/450 RAM)
        remaining devices SMALL (1200 CPU, 512 RAM, distr: 800/400 CPU, 300/200 RAM)
    The application installed is always the same (100 CPU, 32 RAM)

    This scanario, moreover, permits to define with amount of deployments has
    to be considered with JobIntensivity.HEAVY
    """

    application: ApplicationApi
    my_apps_mapping: Dict[str, MyApp]

    def __init__(
        self,
        dump_file: Optional[str],
        fog_director_api_url: Optional[str],
        max_simulation_iterations: Optional[int],
        number_of_devices: int,
        number_of_deployments: int,
        percentage_of_heavy_job: int,
        verbose: bool,
    ):
        super(SmartResort, self).__init__(
            dump_file=dump_file,
            fog_director_api_url=fog_director_api_url,
            max_simulation_iterations=max_simulation_iterations,
            verbose=verbose,
        )
        self.number_of_devices = number_of_devices
        self.number_of_deployments = number_of_deployments
        self.percentage_of_heavy_job = percentage_of_heavy_job

        big_devices = [
            Device(
                deviceId=f'dev-{device_number}',
                ipAddress=f'10.10.20.5{device_number}',
                port='8443',
                username='username',
                password='password',
                totalCPU=2500,
                _cpuMetricsDistributionMean=1700,
                _cpuMetricsDistributionStdDev=500,
                totalMEM=1024,
                _memMetricsDistributionMean=850,
                _memMetricsDistributionStdDev=450,
                chaosDieProb=0,
                chaosReviveProb=1,
            ) for device_number in range(1, 6)
        ]

        medium_devices = [
            Device(
                deviceId=f'dev-{device_number}',
                ipAddress=f'10.10.20.5{device_number}',
                port='8443',
                username='username',
                password='password',
                totalCPU=1500,
                _cpuMetricsDistributionMean=1000,
                _cpuMetricsDistributionStdDev=400,
                totalMEM=1024,
                _memMetricsDistributionMean=750,
                _memMetricsDistributionStdDev=450,
                chaosDieProb=0,
                chaosReviveProb=1,
            ) for device_number in range(6, 11)
        ]

        small_devices = [
            Device(
                deviceId=f'dev-{device_number}',
                ipAddress=f'10.10.20.5{device_number}',
                port='8443',
                username='username',
                password='password',
                totalCPU=1200,
                _cpuMetricsDistributionMean=800,
                _cpuMetricsDistributionStdDev=400,
                totalMEM=512,
                _memMetricsDistributionMean=300,
                _memMetricsDistributionStdDev=200,
                chaosDieProb=0,
                chaosReviveProb=1,
            ) for device_number in range(11, number_of_devices + 1)
        ]

        self.scenario_devices.extend(big_devices)
        self.scenario_devices.extend(medium_devices)
        self.scenario_devices.extend(small_devices)

    @classmethod
    def _cli_parser(cls) -> ArgumentParser:
        parser = super(SmartResort, cls)._cli_parser()
        parser.add_argument(
            '--number-of-devices',
            dest='number_of_devices',
            type=positive_int,
            default=15,
            help='Number of devices to simulate. (default: %(default)s)',
        )
        parser.add_argument(
            '--number-of-deployments',
            dest='number_of_deployments',
            type=positive_int,
            default=30,
            help='Number of deployments to simulate. (default: %(default)s)',
        )
        parser.add_argument(
            '--percentage-of-heavy-jobs',
            dest='percentage_of_heavy_job',
            type=percentage,
            default=0,
            help='Percentage of heavy jobs (default: %(default)s)',
        )
        return parser

    @classmethod
    def _init_from_cli_args(cls, args: Namespace) -> 'SmartResort':
        return cls(
            dump_file=args.dump_file,
            fog_director_api_url=args.fog_director_api_url,
            max_simulation_iterations=args.max_simulation_iterations,
            number_of_deployments=args.number_of_deployments,
            number_of_devices=args.number_of_devices,
            percentage_of_heavy_job=args.percentage_of_heavy_job,
            verbose=args.verbose,
        )

    def _get_best_fit_device(self, cpu_required: float, mem_required: float) -> Optional[Dict[str, Any]]:
        devices = self.fog_director_client.get_devices()
        devices = [
            dev
            for dev in devices['data']
            if (
                dev['capabilities']['nodes'][0]['cpu']['available'] >= cpu_required
                and dev['capabilities']['nodes'][0]['memory']['available'] >= mem_required
            )
        ]
        devices.sort(
            reverse=True,
            key=lambda dev: (dev['capabilities']['nodes'][0]['cpu']['available'], dev['capabilities']['nodes'][0]['memory']['available']),
        )
        return next(iter(devices))

    def _get_best_fit_device_until_success(self, cpu_required: float, mem_required: float, max_trial: int = 1000) -> str:
        count = 0
        while max_trial is None or count < max_trial:
            device = self._get_best_fit_device(cpu_required, mem_required)
            if device is not None:
                return device['deviceId']
        raise RuntimeError('Too many iterations without finding a suitable device.')

    def configure_infrastructure(self) -> None:
        # Adding Devices to FogDirector
        self.register_devices(*self.scenario_devices)

        # Uploading .tar.gz
        self.application = self.register_application('NettestApp2V1_lxc.tar.gz')

        self.my_apps_mapping = {}

        for deployment_id in range(0, self.number_of_deployments):
            # Creating myApp
            my_app = MyApp(
                name=f'SmartResortApplication {deployment_id}',
                applicationLocalAppId=self.application['localAppId'],
                applicationVersion=self.application['version'],
            )
            self.my_apps_mapping[my_app.name] = my_app
            self.register_my_apps(my_app)

            self.install_my_app(
                my_app_id=my_app.myAppId,
                device_id=self._get_best_fit_device_until_success(self.application['cpuUsage'], self.application['memoryUsage']),
            )
            self.start_my_app(my_app.myAppId)

    def manage_iteration(self) -> None:
        already_migrated: Set[str] = set()
        not_reachable_device_my_apps_mapping: DefaultDict[str, List[MyApp]] = defaultdict(list)

        for alert in self.get_all_alerts():
            if alert['type'] in (AlertType.APP_HEALTH.value, AlertType.DEVICE_REACHABILITY.value):
                if alert['appName'] in already_migrated:
                    continue

                already_migrated.add(alert['appName'])
                self.stop_my_app(self.my_apps_mapping[alert['appName']].myAppId)
                self.uninstall_my_app(
                    my_app_id=self.my_apps_mapping[alert['appName']].myAppId,
                    device_ids=[alert['deviceId']],
                )
                self.install_my_app(
                    my_app_id=self.my_apps_mapping[alert['appName']].myAppId,
                    device_id=self._get_best_fit_device_until_success(
                        cpu_required=self.application['cpuUsage'],
                        mem_required=self.application['memoryUsage'],
                    ),
                )
                self.stop_my_app(self.my_apps_mapping[alert['appName']].myAppId)

                if alert['type'] == AlertType.DEVICE_REACHABILITY.value:
                    not_reachable_device_my_apps_mapping[alert['deviceId']].append(self.my_apps_mapping[alert['appName']])

            elif alert['type'] == AlertType.CPU_CRITICAL_CONSUMPTION.value:
                # TODO: To be implemented according new API found
                continue

        devices = self.get_all_devices()
        revived_device_ids = [
            device['deviceId']
            for device in devices
            if device['deviceId'] in not_reachable_device_my_apps_mapping
        ]
        for device_id, my_apps in not_reachable_device_my_apps_mapping.items():
            if device_id not in revived_device_ids:
                continue

            for my_app in my_apps:
                self.uninstall_my_app(
                    my_app_id=my_app.myAppId,
                    device_ids=[device_id],
                )


if __name__ == '__main__':
    instance = SmartResort.get_instance()
    instance.run()
