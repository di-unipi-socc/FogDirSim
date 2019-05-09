import os
from functools import wraps
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar

from bravado.client import SwaggerClient
from bravado.exception import BravadoConnectionError
from bravado.exception import BravadoTimeoutError
from bravado.exception import HTTPError
from requests.auth import _basic_auth_str  # We should be importing a private function, but let's use this for now

from fog_director_simulator.database.models import ApplicationProfile
from fog_director_simulator.database.models import Device
from fog_director_simulator.database.models import JobDeviceAllocation
from fog_director_simulator.database.models import MyApp
from fog_director_simulator.pyramid.fake_fog_director.formatters import AlertApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import ApplicationApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import DeviceResponseApi
from fog_director_simulator.pyramid.fake_fog_director.formatters import JobApi
from fog_director_simulator.pyramid.fake_fog_director.request_types import ApplicationResourceAsk
from fog_director_simulator.pyramid.fake_fog_director.request_types import DeployMyApp
from fog_director_simulator.pyramid.fake_fog_director.request_types import DeviceMinimal
from fog_director_simulator.pyramid.fake_fog_director.request_types import MyAppAction
from fog_director_simulator.pyramid.fake_fog_director.request_types import MyAppActionDeployDevices
from fog_director_simulator.pyramid.fake_fog_director.request_types import MyAppActionDeployItem
from fog_director_simulator.pyramid.fake_fog_director.request_types import MyAppActionUndeployDevices
from fog_director_simulator.pyramid.fake_fog_director.request_types import ResourceAsk
from fog_director_simulator.pyramid.simulator_api.request_types import DeviceDescription


Func = TypeVar('Func', bound=Callable[..., Any])


class retry:

    exceptions: Tuple[Type[BaseException], ...]
    max_retries: int

    def __init__(self, exceptions: Tuple[Type[BaseException], ...], max_retries: int):
        self.exceptions = exceptions
        self.max_retries = max_retries

    def __call__(self, fun: Func) -> Func:
        @wraps(fun)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[BaseException] = None
            for idx in range(1, self.max_retries + 1):
                try:
                    return fun(*args, **kwargs)
                except self.exceptions as exc:
                    print(f'{fun} failed, retry {idx} of {self.max_retries}')
                    last_exception = exc
            assert last_exception
            raise last_exception
        return wrapper  # type: ignore


class ScenarioAPIUtilMixin:
    api_client: Optional[SwaggerClient]
    fog_director_client: SwaggerClient
    fog_director_username = 'username'
    fog_director_password = 'password'
    fog_director_token: str
    scenario_devices: List[Device]

    @property
    def _fog_director_authentication(self) -> Dict[str, Dict[str, str]]:
        return {
            'headers': {
                'X-Token-Id': self.fog_director_token,
            },
        }

    def create_devices(self) -> None:
        """
        Add devices to DB
        """
        if self.api_client is None:
            return
        futures = [
            self.api_client.simulator_management.post_simulator_management_device_v1(
                body=DeviceDescription(
                    deviceId=device.deviceId,
                    ipAddress=device.ipAddress,
                    username=device.username,
                    password=device.password,
                    port=device.port,
                    totalCPU=device.totalCPU,
                    cpuMetricsDistributionMean=device._cpuMetricsDistributionMean,
                    cpuMetricsDistributionStdDev=device._cpuMetricsDistributionStdDev,
                    totalMEM=device.totalMEM,
                    memMetricsDistributionMean=device._memMetricsDistributionMean,
                    memMetricsDistributionStdDev=device._memMetricsDistributionStdDev,
                    chaosDieProb=device.chaosDieProb,
                    chaosReviveProb=device.chaosReviveProb,
                ),
            )
            for device in self.scenario_devices
        ]
        for future in futures:
            future.result()

    @retry(exceptions=(BravadoConnectionError, BravadoTimeoutError), max_retries=32)
    def iteration_count(self) -> int:
        if self.api_client is None:
            return 0
        return self.api_client.simulator_frontend.get_simulator_frontend_iteration_count_v1().result()['iteration_count']

    @retry(exceptions=(BravadoConnectionError, BravadoTimeoutError), max_retries=32)
    def get_all_devices(self) -> List[DeviceResponseApi]:
        return self.fog_director_client.v1.get_v1_appmgr_devices(
            _request_options=self._fog_director_authentication,
        ).result()["data"]

    @retry(exceptions=(BravadoConnectionError, BravadoTimeoutError), max_retries=32)
    def get_all_alerts(self) -> List[AlertApi]:
        return self.fog_director_client.v1.get_v1_appmgr_alerts(
            _request_options=self._fog_director_authentication,
        ).result()['data']

    # No need to retry as this is part of the infrastructure configuration process
    def register_devices(self, *devices: Device) -> Tuple[Device, ...]:
        futures = {
            (device.ipAddress, device.port): self.fog_director_client.v1.post_v1_appmgr_devices(
                body=DeviceMinimal(
                    port=device.port,
                    ipAddress=device.ipAddress,
                    username=device.username,
                    password=device.password,
                ),
                _request_options=self._fog_director_authentication,
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

    # No need to retry as this is part of the infrastructure configuration process
    def register_my_apps(self, *my_apps: MyApp) -> Tuple[MyApp, ...]:
        futures = {
            my_app.name: self.fog_director_client.v1.post_v1_appmgr_myapps(
                body=DeployMyApp(
                    name=my_app.name,
                    sourceAppName=f'{my_app.applicationLocalAppId}:{my_app.applicationVersion}',
                    version=my_app.applicationVersion,
                    appSourceType='LOCAL_STORE',
                ),
                _request_options=self._fog_director_authentication,
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

    # No need to retry as this is part of the infrastructure configuration process
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
                file=f.read(),
                **{
                    'X-Publish-On-Upload': True,
                },
                _request_options=self._fog_director_authentication,
            ).result()

    @retry(exceptions=(HTTPError, BravadoConnectionError, BravadoTimeoutError), max_retries=32)
    def get_fog_director_token(self) -> str:
        return self.fog_director_client.v1.post_v1_appmgr_tokenservice(
            Authorization=_basic_auth_str(username=self.fog_director_username, password=self.fog_director_password),
        ).result()['token']

    @retry(exceptions=(HTTPError, BravadoConnectionError, BravadoTimeoutError), max_retries=32)
    def install_my_app(self, my_app_id: int, device_id: str) -> JobApi:
        def _build_action_deploy_item(device_allocation: JobDeviceAllocation) -> MyAppActionDeployItem:
            return MyAppActionDeployItem(
                deviceId=device_allocation.deviceId,
                resourceAsk=ResourceAsk(
                    resources=ApplicationResourceAsk(
                        profile=device_allocation.profile.iox_name(),
                        cpu=device_allocation.cpu,
                        memory=device_allocation.memory,
                        network=[  # We do not simulate metrics collection on networking stack
                            {
                                'interface-name': 'eth0',
                                'network-name': 'iox-bridge0',
                            },
                        ],
                    ),
                ),
            )

        device_allocations = [
            JobDeviceAllocation(  # type: ignore
                deviceId=device_id,
                profile=ApplicationProfile.Tiny,
                cpu=100,
                memory=32,
            ),
        ]

        return self.fog_director_client.v1.post_v1_appmgr_myapps_my_app_id_action(
            my_app_id=my_app_id,
            body=MyAppAction(
                deploy=MyAppActionDeployDevices(
                    config={},
                    metricsPollingFrequency='3600000',
                    startApp=True,
                    devices=[
                        _build_action_deploy_item(device_allocation)
                        for device_allocation in device_allocations
                    ],
                ),
            ),
            _request_options=self._fog_director_authentication,
        ).result()

    @retry(exceptions=(BravadoConnectionError, BravadoTimeoutError), max_retries=32)
    def start_my_app(self, my_app_id: int) -> None:
        self.fog_director_client.v1.post_v1_appmgr_myapps_my_app_id_action(
            my_app_id=my_app_id,
            body=MyAppAction(start={}),
            _request_options=self._fog_director_authentication,
        ).result()

    @retry(exceptions=(BravadoConnectionError, BravadoTimeoutError), max_retries=32)
    def stop_my_app(self, my_app_id: int) -> None:
        self.fog_director_client.v1.post_v1_appmgr_myapps_my_app_id_action(
            my_app_id=my_app_id,
            body=MyAppAction(stop={}),
            _request_options=self._fog_director_authentication,
        ).result()

    @retry(exceptions=(BravadoConnectionError, BravadoTimeoutError), max_retries=32)
    def uninstall_my_app(self, my_app_id: int, device_ids: Iterable[str]) -> None:
        self.fog_director_client.v1.post_v1_appmgr_myapps_my_app_id_action(
            my_app_id=my_app_id,
            body=MyAppAction(
                undeploy=MyAppActionUndeployDevices(
                    devices=list(device_ids),
                ),
            ),
            _request_options=self._fog_director_authentication,
        ).result()

    @retry(exceptions=(BravadoConnectionError, BravadoTimeoutError), max_retries=32)
    def simulation_statistics(self, number_of_samplings: int) -> Dict[str, Any]:
        if self.api_client is None:
            return {}
        return self.api_client.simulator_frontend.get_simulator_frontend_simulation_statistic_v1(
            totalNumberOfSamplings=number_of_samplings,
        ).response().incoming_response.json()
