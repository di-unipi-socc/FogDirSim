from collections import defaultdict
from typing import Any
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from fog_director_simulator.database import Device
from fog_director_simulator.database import MyApp
from fog_director_simulator.database.models import Alert
from fog_director_simulator.database.models import AlertType
from fog_director_simulator.database.models import ApplicationProfile
from fog_director_simulator.database.models import JobDeviceAllocation
from fog_director_simulator.scenario.base import BaseScenario


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

    def __init__(
        self,
        number_of_devices: int = 15,
        number_of_deployments: int = 30,
        percentage_of_heavy_job: int = 0,
        max_simulation_iterations: Optional[int] = None,
        fog_director_api: Optional[str] = None,
    ):
        self.number_of_devices = number_of_devices
        self.number_of_deployments = number_of_deployments
        self.percentage_of_heavy_job = percentage_of_heavy_job
        BaseScenario.__init__(self, max_simulation_iterations=max_simulation_iterations, fog_director_api=fog_director_api)

        big_devices = [
            Device(
                deviceId=f'dev-{device_number}',
                ipAddress=f'10.10.20.5{device_number}',
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

    def _install_my_app(self, my_app_id: int, device_id: str) -> None:
        self.install_my_app(
            my_app_id=my_app_id,
            device_allocations=[
                JobDeviceAllocation(  # type: ignore
                    deviceId=device_id,
                    profile=ApplicationProfile.Tiny,
                    cpu=100,
                    memory=32,
                ),
            ],
            retry_on_failure=True,
        )

    def configure_infrastructure(self) -> None:
        # Adding Devices to FogDirector
        self.register_devices(*self.scenario_devices)

        # Uploading .tar.gz
        self.application = self.register_application('NettestApp2')

        for deployment_id in range(0, self.number_of_deployments):
            # Creating myApp
            myapp = MyApp(name=f'SmartResortApplication {deployment_id}')
            myapp.applicationLocalAppId = self.application['localAppId']
            self.register_my_apps(myapp)

            self._install_my_app(
                my_app_id=myapp.myAppId,
                device_id=self._get_best_fit_device_until_success(self.application['cpuUsage'], self.application['memoryUsage']),
            )
            self.start_my_apps()

    def manage_iteration(self) -> None:
        alerts = [
            Alert(  # type: ignore
                myAppId=alert['myAppId'],
                deviceId=alert['deviceId'],
                type=alert['type'],
                time=alert['time'],
            )
            for alert in self.fog_director_client.get_alerts().result()['data']
        ]
        already_migrated: Set[int] = set()
        not_reachable_devices: DefaultDict[str, List[int]] = defaultdict(list)
        for alert in alerts:
            if alert.type in (AlertType.APP_HEALTH, AlertType.DEVICE_REACHABILITY):
                if alert.myAppId in already_migrated:
                    continue

                already_migrated.add(alert.myAppId)
                self.stop_my_apps(alert.myAppId)
                self.uninstall_my_app(my_app_id=alert.myAppId, device_ids=[alert.deviceId])
                self._install_my_app(
                    my_app_id=alert.myAppId,
                    device_id=self._get_best_fit_device_until_success(
                        # TODO: this has to be fixed, via the API we do not have application available
                        alert.myApp.application.cpuUsage,
                        alert.myApp.application.memoryUsage,
                    ),
                )
                self.stop_my_apps(alert.myAppId)
                if alert.type == AlertType.DEVICE_REACHABILITY:
                    not_reachable_devices[alert.deviceId].append(alert.myAppId)

            elif alert.type == AlertType.CPU_CRITICAL_CONSUMPTION:
                # TODO: To be implemented according new API found
                continue

        devices = self.get_all_devices()
        revived_device_ids = [
            device['deviceId']
            for device in devices
            if device['deviceId'] in not_reachable_devices
        ]
        for device_id, my_app_ids in not_reachable_devices.items():
            if device_id not in revived_device_ids:
                continue
            for my_app_id in my_app_ids:
                self.uninstall_my_app(my_app_id=my_app_id, device_ids=[device_id])
