from typing import Any
from typing import Dict

from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.database.models import Alert


def _format(alert: Alert) -> Dict[str, Any]:
    return {
        'myAppId': alert.myAppId,
        'deviceId': alert.deviceId,
        'type': alert.type.name,
        'time': alert.time,
    }


@view_config(route_name='api.v1.appmgr.alerts')
def v1_appmgr_alerts(request: Request) -> Dict[str, Any]:
    return {
        'data': [
            _format(alert)
            for alert in request.database_logic.get_alerts(request.simulation_time)
        ]
    }
