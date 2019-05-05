from typing import Any
from typing import Dict

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

from fog_director_simulator.database.models import ApplicationProfile
from fog_director_simulator.database.models import Device
from fog_director_simulator.database.models import Job
from fog_director_simulator.database.models import JobDeviceAllocation
from fog_director_simulator.database.models import JobIntensivity
from fog_director_simulator.database.models import JobStatus
from fog_director_simulator.database.models import MyApp
from fog_director_simulator.pyramid.fake_fog_director.formatters import job_format
from fog_director_simulator.pyramid.fake_fog_director.formatters import JobApi


def _do_start(my_app: MyApp) -> Job:
    if not my_app.jobs:
        raise HTTPBadRequest()

    for job in my_app.jobs:  # type: ignore
        if job.status not in {JobStatus.DEPLOY, JobStatus.START}:
            raise HTTPBadRequest()
        job.status = JobStatus.START

    return my_app.jobs[0]  # type: ignore # NOTE: the real fog-director does create a new job, we're not willing to do it for simulation proposes


def _do_stop(my_app: MyApp) -> Job:
    if not my_app.jobs:
        raise HTTPBadRequest()

    for job in my_app.jobs:  # type: ignore
        if job.status != JobStatus.START:
            raise HTTPBadRequest()
        job.status = JobStatus.STOP

    return my_app.jobs[0]  # type: ignore # NOTE: the real fog-director does create a new job, we're not willing to do it for simulation proposes


def _do_deploy(my_app: MyApp, job_intensivity: JobIntensivity, myAppActionDeploy: Dict[str, Any], devices: Dict[str, Device]) -> Job:
    job = Job(  # type: ignore
        myApp=my_app,
        status=JobStatus.DEPLOY,
        profile=job_intensivity,
        job_device_allocations=[],
    )

    job_device_allocations = []
    for deploy_device in myAppActionDeploy['devices']:
        device = devices[deploy_device['deviceId']]

        if not device.isAlive:
            raise HTTPBadRequest()

        cpu_demand = deploy_device['resourceAsk']['resources']['cpu']
        device.reservedCPU += cpu_demand
        if device.totalCPU < device.reservedCPU:
            raise HTTPBadRequest()

        mem_demand = deploy_device['resourceAsk']['resources']['memory']
        device.reservedMEM += mem_demand
        if device.totalMEM < device.reservedMEM:
            raise HTTPBadRequest()

        job_device_allocations.append(
            JobDeviceAllocation(  # type: ignore
                device=device,
                job=job,
                profile=ApplicationProfile.from_iox_name(deploy_device['resourceAsk']['resources']['profile']),
                cpu=cpu_demand,
                memory=mem_demand,
            ),
        )

    job.job_device_allocations.extend(job_device_allocations)  # type: ignore
    return job


def _do_undeploy(my_app: MyApp, devices: Dict[str, Device]) -> Job:
    for job in my_app.jobs:  # type: ignore
        if job.status == JobStatus.UNINSTALLED:
            continue
        to_remove = []
        for job_device_allocation in job.job_device_allocations:
            if job_device_allocation.deviceId not in devices:
                continue
            job_device_allocation.device.reservedCPU += job_device_allocation.cpu
            job_device_allocation.device.reservedMEM += job_device_allocation.memory
            to_remove.append(job_device_allocation)

        # This is ugly and requires some care :)
        job.job_device_allocations = [
            job_device_allocation
            for job_device_allocation in job.job_device_allocations
            if job_device_allocation not in to_remove
        ]
        job.status = JobStatus.UNINSTALLED

    return my_app.jobs[0]  # type: ignore # NOTE: the real fog-director does create a new job, we're not willing to do it for simulation proposes


@view_config(route_name='api.v1.appmgr.myapps.my_app_id.action', request_method='POST')
def post_v1_appmgr_myapps_my_app_id_action(request: Request) -> JobApi:
    try:
        my_app = request.database_logic.get_my_app(myAppId=request.swagger_data['my_app_id'])
    except NoResultFound:
        raise HTTPNotFound()

    if not my_app.application.isPublished:
        raise HTTPBadRequest()

    job_intensivity = JobIntensivity[request.swagger_data['job_intensivity'].upper()]
    body = request.swagger_data['body']

    if body['start'] is not None:
        job = _do_start(my_app=my_app)
    elif body['stop'] is not None:
        job = _do_stop(my_app=my_app)
    elif body['deploy'] is not None:
        job = _do_deploy(
            my_app=my_app,
            job_intensivity=job_intensivity,
            myAppActionDeploy=body['deploy'],
            devices={
                deploy_device['deviceId']: request.database_logic.get_device(deviceId=deploy_device['deviceId'])
                for deploy_device in body['deploy']['devices']
            },
        )
        request.database_logic.create(job)
    elif body['undeploy'] is not None:
        job = _do_undeploy(
            my_app=my_app,
            devices={
                device_id: request.database_logic.get_device(deviceId=device_id)
                for device_id in body['undeploy']['devices']
            },
        )
    else:
        raise HTTPBadRequest()

    return job_format(job)
