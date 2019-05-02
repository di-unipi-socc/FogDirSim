from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.pyramid.fake_fog_director.formatters import application_format
from fog_director_simulator.pyramid.fake_fog_director.formatters import ApplicationResponse


@view_config(route_name='api.v1.appmgr.localapps', request_method='GET')
def get_v1_appmgr_localapps(request: Request) -> ApplicationResponse:
    return ApplicationResponse(
        data=[
            application_format(application)
            for application in request.database_logic.get_applications()
        ],
    )
