from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.pyramid.simulator_api.formatters import iteration_count_format
from fog_director_simulator.pyramid.simulator_api.formatters import IterationCountApi


@view_config(route_name='api.simulator_frontend.iteration_count.v1', request_method='GET')
def get_simulator_frontend_iteration_count_v1(request: Request) -> IterationCountApi:
    return iteration_count_format(request.simulation_time)
