from typing import Optional

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
        super(FogDirMime, self).__init__(
            dump_file=dump_file,
            fog_director_api_url=fog_director_api_url,
            max_simulation_iterations=max_simulation_iterations,
            verbose_all=verbose_all,
            verbose_fog_director_api=verbose_fog_director_api,
            verbose_simulator_api=verbose_simulator_api,
            verbose_simulator_engine=verbose_simulator_engine,
        )
        self.is_building_my_app_ever_moved = False

    def configure_infrastructure(self) -> None:
        for current_device in self.scenario_devices:
            self.register_device(current_device)

        application = self.register_application('NettestApp2V1_lxc.tar.gz')
        # TODO: publish application

        self.building_my_app.applicationLocalAppId = application['localAppId']
        self.building_my_app.applicationVersion = application['version']
        self.apartment_my_app.applicationLocalAppId = application['localAppId']
        self.apartment_my_app.applicationVersion = application['version']
        self.register_my_app(self.building_my_app)
        self.register_my_app(self.apartment_my_app)
        self.install_my_app(
            my_app_id=self.building_my_app.myAppId,
            device_id=self.fog_1.deviceId,
        )
        self.install_my_app(
            my_app_id=self.apartment_my_app.myAppId,
            device_id=self.fog_2.deviceId,
        )
        self.start_my_app(self.building_my_app.myAppId)
        self.start_my_app(self.apartment_my_app.myAppId)

    def manage_iteration(self) -> None:
        for alert in self.get_all_alerts():
            if alert['type'] != AlertType.APP_HEALTH.name:
                continue

            if alert['appName'] == self.building_my_app.name and not self.is_building_my_app_ever_moved:
                self.stop_my_app(self.building_my_app.myAppId)
                self.uninstall_my_app(self.building_my_app.myAppId, device_ids=[self.fog_1.deviceId])
                self.install_my_app(
                    my_app_id=self.building_my_app.myAppId,
                    device_id=self.fog_3.deviceId,
                )
                self.start_my_app(self.building_my_app.myAppId)
                self.is_building_my_app_ever_moved = True

            elif alert['appName'] == self.apartment_my_app.name:
                isOnFog1 = alert['deviceId'] == self.fog_1.deviceId
                self.stop_my_app(self.apartment_my_app.myAppId)
                self.uninstall_my_app(
                    my_app_id=self.apartment_my_app.myAppId,
                    device_ids=[
                        self.fog_1.deviceId if isOnFog1 else self.fog_2.deviceId
                    ],
                )
                self.install_my_app(
                    my_app_id=self.apartment_my_app.myAppId,
                    device_id=(
                        self.fog_2.deviceId if isOnFog1 else self.fog_1.deviceId
                    ),
                )
                self.start_my_app(self.apartment_my_app.myAppId)


if __name__ == '__main__':
    instance = FogDirMime.get_instance()
    instance.run()
