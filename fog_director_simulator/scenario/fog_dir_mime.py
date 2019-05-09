from typing import Set

from fog_director_simulator.database import Device
from fog_director_simulator.database import MyApp
from fog_director_simulator.database.models import AlertType
from fog_director_simulator.scenario.base import BaseScenario


class FogDirMime(BaseScenario):
    """
    TODO: describe the scenario
    """

    fog_1 = Device(
        deviceId='dev-1',
        ipAddress='10.10.20.51',
        port='8443',
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
        port='8443',
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
        port='8443',
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

    def configure_infrastructure(self) -> None:
        self.register_devices(*self.scenario_devices)

        application = self.register_application('NettestApp2V1_lxc.tar.gz')
        # TODO: publish application

        self.building_my_app.applicationLocalAppId = application['localAppId']
        self.building_my_app.applicationVersion = application['version']
        self.apartment_my_app.applicationLocalAppId = application['localAppId']
        self.apartment_my_app.applicationVersion = application['version']

        self.register_my_apps(self.building_my_app, self.apartment_my_app)

        self.install_my_app(
            my_app_id=self.building_my_app.myAppId,
            device_id=self.fog_1.deviceId,
            retry_on_failure=True,
        )
        self.install_my_app(
            my_app_id=self.apartment_my_app.myAppId,
            device_id=self.fog_2.deviceId,
            retry_on_failure=True,
        )
        self.start_my_apps(self.building_my_app.myAppId, self.apartment_my_app.myAppId)

    def manage_iteration(self) -> None:
        moved_apps: Set[int] = set()
        for alert in self.get_all_alerts():
            if alert['type'] != AlertType.APP_HEALTH:
                continue

            if alert['appName'] == self.building_my_app.name and alert['appName'] not in moved_apps:
                self.stop_my_apps(self.building_my_app.myAppId)
                self.uninstall_my_app(self.building_my_app.myAppId, device_ids=[self.fog_1.deviceId])
                self.install_my_app(
                    my_app_id=self.building_my_app.myAppId,
                    device_id=self.fog_3.deviceId,
                    retry_on_failure=True,
                )
                self.start_my_apps(self.building_my_app.myAppId)
                moved_apps.add(self.building_my_app.myAppId)

            elif alert['appName'] == self.apartment_my_app.name:
                isOnFog1 = alert['deviceId'] == self.fog_1.deviceId
                self.stop_my_apps(self.apartment_my_app.myAppId)
                self.uninstall_my_app(self.apartment_my_app.myAppId, device_ids=[
                    self.fog_1.deviceId if isOnFog1 else self.fog_2.deviceId
                ])
                self.install_my_app(
                    my_app_id=self.apartment_my_app.myAppId,
                    device_id=(
                        self.fog_2.deviceId if isOnFog1 else self.fog_1.deviceId
                    ),
                    retry_on_failure=True,
                )
                self.start_my_apps(self.apartment_my_app.myAppId)
                moved_apps.add(self.apartment_my_app.myAppId)


if __name__ == '__main__':
    instance = FogDirMime.get_instance()
    instance.run()
