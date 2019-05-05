from typing import cast

from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

from fog_director_simulator.database.models import ApplicationProfile
from fog_director_simulator.pyramid.fake_fog_director.formatters import application_format
from fog_director_simulator.pyramid.fake_fog_director.formatters import ApplicationApi
from fog_director_simulator.pyramid.fake_fog_director.request_types import LocalApp


@view_config(route_name='api.v1.appmgr.localapps.local_application_id_version', request_method='PUT')
def put_v1_appmgr_localapps_local_application_id_version(request: Request) -> ApplicationApi:
    body = cast(LocalApp, request.swagger_data['body'])

    try:
        application = request.database_logic.get_application(
            localAppId=request.swagger_data['local_application_id'],
            version=request.swagger_data['version'],
        )
    except NoResultFound:
        raise HTTPNotFound()

    application.localAppId = body['localAppId']
    application.version = body['version']
    application.isPublished = (body['published'] == 'published')
    application.profileNeeded = ApplicationProfile.from_iox_name(body['profileNeeded'])
    if application.profileNeeded == ApplicationProfile.Custom:
        application._cpuUsage = body['cpuUsage']
        application._memoryUsage = body['memoryUsage']
    else:
        application._cpuUsage = None
        application._memoryUsage = None

    return application_format(application)
