from collections import defaultdict
from typing import cast, List

from fog_director_simulator.database import Device, MyApp
from fog_director_simulator.database.models import JobDeviceAllocation, ApplicationProfile, Alert, AlertType
from fog_director_simulator.scenario.base import BaseScenario


class Optional(object):
    pass


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

    def _get_best_fit_device(self, cpu_required, mem_required):
        devices = self.fog_director_client.get_devices()
        devices = [dev
                   for dev in devices["data"]
                   if dev["capabilities"]["nodes"][0]["cpu"]["available"] >= cpu_required
                   and dev["capabilities"]["nodes"][0]["memory"]["available"] >= mem_required]
        devices.sort(reverse=True, key=(lambda dev: (dev["capabilities"]["nodes"][0]["cpu"]["available"],
                                                     dev["capabilities"]["nodes"][0]["memory"]["available"])))
        return None if len(devices) == 0 else devices[0]

    def _get_best_fit_device_until_success(self, cpu_required, mem_required, max_trial = None):
        device = None
        count = 0
        while not device and (max_trial is None or count < max_trial):
            device = self._get_best_fit_device(cpu_required, mem_required)
        return device

    def __init__(self,
                 number_of_devices: int = 15,
                 number_of_deployments: int = 30,
                 percentage_of_heavy_job: int = 0,
                 max_simulation_iterations: Optional[int] = None, 
                 fog_director_api: Optional[str] = None,
                 ):
        self.number_of_devices = number_of_devices
        self.number_of_deployments = number_of_deployments
        self.percentage_of_heavy_job = percentage_of_heavy_job
        BaseScenario.__init__(self, max_simulation_iterations=max_simulation_iterations, fog_director_api= fog_director_api)

        big_devices = [
            Device(
                deviceId='dev-{}'.format(dev_number),
                ipAddress='10.10.20.5{}'.format(dev_number),
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
            ) for dev_number in range(1, 6)
        ]

        medium_devices = [
            Device(
                deviceId='dev-{}'.format(dev_number),
                ipAddress='10.10.20.5{}'.format(dev_number),
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
            ) for dev_number in range(6, 11)
        ]

        small_devices = [
            Device(
                deviceId='dev-{}'.format(dev_number),
                ipAddress='10.10.20.5{}'.format(dev_number),
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
            ) for dev_number in range(11, number_of_devices + 1)
        ]

        self.scenario_devices.extend(big_devices)
        self.scenario_devices.extend(medium_devices)
        self.scenario_devices.extend(small_devices)

    def _install_my_app(self, my_app: MyApp, device: Device):
        self.install_my_app(
            my_app=my_app,
            device_allocations=[
                JobDeviceAllocation(
                    device=device,
                    profile=ApplicationProfile.Tiny,
                    cpu=100,
                    memory=32,
                ),
            ],
            retry_on_failure=True,
        )

    def configure_infrastructure(self):
        # Adding Devices to FogDirector
        self.register_devices(*self.scenario_devices)

        # Uploading .tar.gz
        application = self.register_application('NettestApp2')

        for i in range(0, self.number_of_deployments):
            # Creating myApp
            myapp = MyApp("SmartResortApplication {}".format(i))
            myapp.applicationLocalAppId = application.localAppId
            self.register_my_apps(myapp)

            self._install_my_app(
                my_app=myapp,
                device=self._get_best_fit_device_until_success(application.cpuUsage, application.memoryUsage),
            )
            self.start_my_apps()

    def manage_iteration(self):
        alerts = cast(List[Alert], self.fog_director_client.get_alerts().result()['data'])
        already_migrated = []
        not_reachable_devices = defaultdict(lambda _: [])
        for alert in alerts:
            if alert.type in (AlertType.APP_HEALTH, AlertType.DEVICE_REACHABILITY):
                if alert.myAppId in already_migrated:
                    continue
                else:
                    already_migrated.append(alert.myAppId)
                self.stop_my_apps(alert.myApp)
                self.uninstall_my_app(alert.myApp, devices=[alert.device])
                self._install_my_app(
                    my_app=alert.myApp,
                    device=self._get_best_fit_device_until_success(
                        alert.myApp.application.cpuUsage,
                        alert.myApp.application.memoryUsage
                    )
                )
                self.stop_my_apps(alert.myApp)
                if alert.type == AlertType.DEVICE_REACHABILITY:
                    not_reachable_devices[alert.deviceId].append(alert.myApp)
            elif alert.type == AlertType.CPU_CRITICAL_CONSUMPTION:
                # TODO: To be implemented according new API found
                continue

        devices = self.get_all_devices()
        revived_devices = [dev for dev in devices if dev.deviceId in not_reachable_devices]
        for device in revived_devices:
            for myApp in not_reachable_devices[device.deviceId]:
                self.uninstall_my_app(my_app=myApp, devices=[device])
        not_reachable_devices.clear()

