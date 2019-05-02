from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

from fog_director_simulator.database.models import JobStatus
from fog_director_simulator.pyramid.fake_fog_director.formatters import myapp_format
from fog_director_simulator.pyramid.fake_fog_director.formatters import MyAppApi


@view_config(route_name='api.v1.appmgr.myapps.my_app_id', request_method='DELETE')
def delete_v1_appmgr_myapps_my_app_id(request: Request) -> MyAppApi:
    try:
        my_app = request.database_logic.get_my_app(myAppId=request.swagger_data['my_app_id'])
    except NoResultFound:
        raise HTTPNotFound

    if any(
        job.status != JobStatus.UNINSTALLED
        for job in my_app.jobs
    ):
        raise HTTPForbidden

    my_app.destructionTime = request.simulation_time

    return myapp_format(my_app)
