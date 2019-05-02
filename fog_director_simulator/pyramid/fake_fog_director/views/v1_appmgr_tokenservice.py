from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.pyramid.fake_fog_director.formatters import TokenServiceApi


@view_config(route_name='api.v1.appmgr.tokenservice', request_method='POST')
def post_v1_appmgr_tokenservice(request: Request) -> TokenServiceApi:
    return TokenServiceApi(
        token='string',
        expiryTime=0,
        serverEpochTime=0,
    )
