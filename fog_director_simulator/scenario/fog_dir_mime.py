from typing import Set

from fog_director_simulator.database import Device
from fog_director_simulator.database import MyApp
from fog_director_simulator.database.models import Alert
from fog_director_simulator.database.models import AlertType
from fog_director_simulator.database.models import ApplicationProfile
from fog_director_simulator.database.models import JobDeviceAllocation
from fog_director_simulator.scenario.base import BaseScenario


class FogDirMime(BaseScenario):
    """
    TODO: describe the scenario
    """

    fog_1 = Device(
        deviceId='dev-1',
        ipAddress='10.10.20.51',
        username='username',
        password='password',
        totalCPU=200,
        _cpuMetricsDistributionMean=180,
        _cpuMetricsDistributionStdDev=40,
        totalMEM=64,
        _memMetricsDistributionMean=56,
        _memMetricsDistributionStdDev=17,
        chaosDieProb=0,
        chaosReviveProb=1,
    )
    fog_2 = Device(
        deviceId='dev-2',
        ipAddress='10.10.20.52',
        username='username',
        password='password',
        totalCPU=200,
        _cpuMetricsDistributionMean=190,
        _cpuMetricsDistributionStdDev=30,
        totalMEM=128,
        _memMetricsDistributionMean=106,
        _memMetricsDistributionStdDev=32,
        chaosDieProb=0,
        chaosReviveProb=1,
    )
    fog_3 = Device(
        deviceId='dev-3',
        ipAddress='10.10.20.53',
        username='username',
        password='password',
        totalCPU=400,
        _cpuMetricsDistributionMean=330,
        _cpuMetricsDistributionStdDev=80,
        totalMEM=128,
        _memMetricsDistributionMean=118,
        _memMetricsDistributionStdDev=21,
        chaosDieProb=0,
        chaosReviveProb=1,
    )

    building_my_app = MyApp(name='Deployment-1')
    apartment_my_app = MyApp(name='Deployment-2')

    scenario_devices = [fog_1, fog_2, fog_3]

    def _install_my_app(self, my_app: MyApp, device: Device) -> None:
        self.install_my_app(
            my_app_id=my_app.myAppId,
            device_allocations=[
                JobDeviceAllocation(  # type: ignore
                    device=device,
                    profile=ApplicationProfile.Tiny,
                    cpu=100,
                    memory=32,
                ),
            ],
            retry_on_failure=True,
        )

    def configure_infrastructure(self) -> None:
        self.register_devices(*self.scenario_devices)

        application = self.register_application('NettestApp2')
        self.building_my_app.applicationLocalAppId = application['localAppId']
        self.building_my_app.applicationVersion = application['version']
        self.apartment_my_app.applicationLocalAppId = application['localAppId']
        self.apartment_my_app.applicationVersion = application['version']

        self.register_my_apps(self.building_my_app, self.apartment_my_app)

        self._install_my_app(my_app=self.building_my_app, device=self.fog_1)
        self._install_my_app(my_app=self.apartment_my_app, device=self.fog_2)
        self.start_my_apps(self.building_my_app.myAppId, self.apartment_my_app.myAppId)

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

        moved_apps: Set[int] = set()
        for alert in alerts:
            if alert.type != AlertType.APP_HEALTH:
                continue

            if alert.myAppId == self.building_my_app.myAppId and alert.myAppId not in moved_apps:
                self.stop_my_apps(self.building_my_app.myAppId)
                self.uninstall_my_app(self.building_my_app.myAppId, device_ids=[self.fog_1.deviceId])
                self._install_my_app(my_app=self.building_my_app, device=self.fog_3)
                self.start_my_apps(self.building_my_app.myAppId)
                moved_apps.add(self.building_my_app.myAppId)

            elif alert.myAppId == self.apartment_my_app.name:
                isOnFog1 = alert.deviceId == self.fog_1.deviceId
                self.stop_my_apps(self.apartment_my_app.myAppId)
                self.uninstall_my_app(self.apartment_my_app.myAppId, device_ids=[
                    self.fog_1.deviceId if isOnFog1 else self.fog_2.deviceId
                ])
                self._install_my_app(my_app=self.apartment_my_app, device=(
                    self.fog_2 if isOnFog1 else self.fog_1
                ))
                self.start_my_apps(self.apartment_my_app.myAppId)
                moved_apps.add(self.apartment_my_app.myAppId)


if __name__ == '__main__':
    instance = FogDirMime.get_instance()
    instance.run()
