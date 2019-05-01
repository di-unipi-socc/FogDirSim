from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.pyramid.fake_fog_director.formatters import application_format


@view_config(route_name='api.v1.appmgr.localapps', request_method='GET')
def get_v1_appmgr_localapps(request: Request) -> Dict[str, Any]:
    return {
        'data': [
            application_format(application)
            for application in request.database_logic.get_applications()
        ]
    }
