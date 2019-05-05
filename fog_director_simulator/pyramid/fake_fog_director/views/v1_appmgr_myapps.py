from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPConflict
from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.database.models import MyApp
from fog_director_simulator.pyramid.fake_fog_director.formatters import myapp_format
from fog_director_simulator.pyramid.fake_fog_director.formatters import MyAppApi


@view_config(route_name='api.v1.appmgr.myapps', request_method='POST')
def post_v1_appmgr_myapps(request: Request) -> MyAppApi:
    minjobs = request.swagger_data['minjobs']
    name = request.swagger_data['body']['name']
    sourceAppName = request.swagger_data['body']['sourceAppName']
    version = request.swagger_data['body']['version']

    if not sourceAppName.endswith(f':{version}'):
        raise HTTPBadRequest()  # NOTE: This is a personal interpretation, the real specs would just create it :(

    if request.database_logic.get_my_app_by_name(name=name):
        raise HTTPConflict()

    local_app_id = sourceAppName[:-len(version) - 1]
    my_app = MyApp(
        applicationLocalAppId=local_app_id,
        applicationVersion=version,
        name=name,
        minJobReplicas=minjobs,
        creationTime=request.simulation_time,
    )
    request.database_logic.create(my_app)

    return myapp_format(my_app)


@view_config(route_name='api.v1.appmgr.myapps', request_method='GET')
def get_v1_appmgr_myapps(request: Request) -> None:
    raise NotImplementedError()
