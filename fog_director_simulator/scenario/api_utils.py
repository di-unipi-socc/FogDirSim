import os
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

from bravado.client import SwaggerClient
from bravado.exception import HTTPError

from fog_director_simulator.database.models import Device
from fog_director_simulator.database.models import JobDeviceAllocation
from fog_director_simulator.database.models import MyApp
from fog_director_simulator.pyramid.fake_fog_director.formatters import AlertApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import ApplicationApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import DeviceApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import JobApi


class ScenarioAPIUtilMixin:
    api_client: Optional[SwaggerClient]
    fog_director_client: SwaggerClient
    scenario_devices: List[Device]

    def create_devices(self) -> None:
        """
        Add devices to DB
        """
        if self.api_client is None:
            return
        futures = [
            self.api_client.simulator_management.post_simulator_management_device_v1(
                body={
                    'deviceId': device.deviceId,
                    'ipAddress': device.ipAddress,
                    'username': device.username,
                    'password': device.password,
                    'port': device.port,
                    'totalCPU': device.totalCPU,
                    'cpuMetricsDistributionMean': device._cpuMetricsDistributionMean,
                    'cpuMetricsDistributionStdDev': device._cpuMetricsDistributionStdDev,
                    'totalMEM': device.totalMEM,
                    'memMetricsDistributionMean': device._memMetricsDistributionMean,
                    'memMetricsDistributionStdDev': device._memMetricsDistributionStdDev,
                    'chaosDieProb': device.chaosDieProb,
                    'chaosReviveProb': device.chaosReviveProb,
                },
            )
            for device in self.scenario_devices
        ]
        for future in futures:
            future.result()

    @property
    def iteration_count(self) -> int:
        raise NotImplementedError(self.api_client)  # TODO: connect the real endpoint

    def get_all_devices(self) -> List[DeviceApi]:
        return self.fog_director_client.v1.get_v1_appmgr_devices().result()["data"]

    def get_all_alerts(self) -> List[AlertApi]:
        return self.fog_director_client.v1.get_v1_appmgr_alerts().result()['data']

    def register_devices(self, *devices: Device) -> Tuple[Device, ...]:
        futures = {
            (device.ipAddress, device.port): self.fog_director_client.register_device_v1(
                body={
                    'port': device.port,
                    'ipAddress': device.ipAddress,
                    'username': device.username,
                    'password': device.password,
                },
            )
            for device in devices
        }

        device_ipAddress_port_deviceId_mapping = {
            key: future.result().deviceId
            for key, future in futures.items()
        }

        for device in devices:
            device.deviceId = device_ipAddress_port_deviceId_mapping[(device.ipAddress, device.port)]
        return devices

    def register_my_apps(self, *my_apps: MyApp) -> Tuple[MyApp, ...]:
        futures = {
            my_app.name: self.fog_director_client.v1.post_v1_appmgr_myapps(
                body={
                    'name': my_app.name,
                    'sourceAppName': my_app.applicationLocalAppId,
                    'version': my_app.applicationVersion,
                    'appSourceType': 'LOCAL_STORE',
                },
            )
            for my_app in my_apps
        }
        # TODO: make it resilient to errors
        my_app_name_id_mapping = {
            name: future.result()['myAppId']
            for name, future in futures.items()
        }

        for my_app in my_apps:
            my_app.myAppId = my_app_name_id_mapping[my_app.name]

        return my_apps

    def register_application(self, application_name: str) -> ApplicationApi:
        with open(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'fog_director_application_archives',
                application_name,
            ),
            mode='rb',
        ) as f:
            return self.fog_director_client.v1.post_v1_appmgr_localapps_upload(
                file=f.read(),  # TODO
            ).result()

    def install_my_app(self, my_app_id: int, device_allocations: Iterable[JobDeviceAllocation], retry_on_failure: bool = False) -> JobApi:
        def _build_device_allocation(device_allocation: JobDeviceAllocation) -> Dict[str, Any]:
            return {
                'deviceId': device_allocation.deviceId,
                'resourceAsk': {
                    'resources': {
                        'profile': device_allocation.profile.iox_name(),
                        'cpu': device_allocation.cpu,
                        'memory': device_allocation.memory,
                        'network': [  # We do not simulate metrics collection on networking stack
                            {
                                'interface-name': 'eth0',
                                'network-name': 'iox-bridge0',
                            },
                        ],
                    },
                },
            }

        try:
            return self.fog_director_client.v1.post_v1_appmgr_myapps_my_app_id_action(
                my_app_id=my_app_id,
                body={
                    'deploy': {
                        'config': {},
                        'metricsPollingFrequency': '3600000',
                        'startApp': True,
                        'devices': [
                            _build_device_allocation(device_allocation)
                            for device_allocation in device_allocations
                        ],
                    },
                },
            ).result()
        except HTTPError:
            if retry_on_failure:
                return self.install_my_app(my_app_id, device_allocations, retry_on_failure)
            else:
                raise

    def start_my_apps(self, *my_app_ids: int) -> None:
        futures = [
            self.fog_director_client.v1.post_v1_appmgr_myapps_my_app_id_action(
                my_app_id=my_app_id,
                body={'start': {}},
            )
            for my_app_id in my_app_ids
        ]

        for future in futures:
            future.result()

    def stop_my_apps(self, *my_app_ids: int) -> None:
        futures = [
            self.fog_director_client.v1.post_v1_appmgr_myapps_my_app_id_action(
                my_app_id=my_app_id,
                body={'stop': {}},
            ).result()
            for my_app_id in my_app_ids
        ]

        for future in futures:
            future.result()

    def uninstall_my_app(self, my_app_id: int, device_ids: Iterable[str]) -> None:
        self.fog_director_client.v1.post_v1_appmgr_myapps_my_app_id_action(
            my_app_id=my_app_id,
            body={
                'undeploy': {
                    'devices': list(device_ids),
                },
            },
        ).result()
