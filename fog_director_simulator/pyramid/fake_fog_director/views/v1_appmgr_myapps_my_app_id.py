from typing import Any
from typing import Dict

from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.database.models import JobStatus
from fog_director_simulator.database.models import MyApp
from fog_director_simulator.pyramid.fake_fog_director.formatters import myapp_format


@view_config(route_name='api.v1.appmgr.myapps.my_app_id', request_method='DELETE')
def delete_v1_appmgr_myapps_my_app_id(request: Request) -> Dict[str, Any]:
    my_app: MyApp = request.database_logic.get_my_app(myAppId=request.swagger_data['my_app_id'])
    if my_app is None:
        raise HTTPNotFound

    if any(
        job.status != JobStatus.UNINSTALLED
        for job in my_app.jobs
    ):
        raise HTTPForbidden

    my_app.destructionTime = request.simulation_time

    return myapp_format(my_app)
