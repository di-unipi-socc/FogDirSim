from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.pyramid.fake_fog_director.formatters import alert_format
from fog_director_simulator.pyramid.fake_fog_director.formatters import AlertsResponse


@view_config(route_name='api.v1.appmgr.alerts', request_method='GET')
def get_v1_appmgr_alerts(request: Request) -> AlertsResponse:
    return AlertsResponse(
        data=[
            alert_format(alert)
            for alert in request.database_logic.get_alerts(request.simulation_time)
        ],
    )
