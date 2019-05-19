import os
from functools import lru_cache

from pyramid.router import Router

from fog_director_simulator.pyramid import default_pyramid_configuration
from fog_director_simulator.pyramid.fake_fog_director import views


@lru_cache(maxsize=1)
def create_application() -> Router:
    """Create the WSGI application, post-fork."""
    config = default_pyramid_configuration(
        root_swagger_spec_path=os.path.join('api_docs', 'fog_director_api', 'swagger.yaml'),
        base_path_api_docs='/api/',
    )

    # Add status metrics view with the internal_ip_only predicate
    config.add_route('api.status', '/status')
    config.add_route('api.status_slow', '/status_slow')
    config.add_route('api.v1.appmgr.alerts', '/api/v1/appmgr/alerts')
    config.add_route('api.v1.appmgr.apps.local_application_id_version', '/api/v1/appmgr/apps/{local_application_id}:{version}')
    config.add_route('api.v1.appmgr.devices', '/api/v1/appmgr/devices')
    config.add_route('api.v1.appmgr.devices.device_id', '/api/v1/appmgr/devices/{device_id}')
    config.add_route('api.v1.appmgr.localapps', '/api/v1/appmgr/localapps')
    config.add_route('api.v1.appmgr.localapps.local_application_id_version', '/api/v1/appmgr/localapps/{local_application_id}:{version}')
    config.add_route('api.v1.appmgr.localapps.upload', '/api/v1/appmgr/localapps/upload')
    config.add_route('api.v1.appmgr.myapps', '/api/v1/appmgr/myapps')
    config.add_route('api.v1.appmgr.myapps.my_app_id', '/api/v1/appmgr/myapps/{my_app_id}')
    config.add_route('api.v1.appmgr.myapps.my_app_id.action', '/api/v1/appmgr/myapps/{my_app_id}/action')
    config.add_route('api.v1.appmgr.tokenservice', '/api/v1/appmgr/tokenservice')
    config.add_route('api.v1.appmgr.tokenservice.token', '/api/v1/appmgr/tokenservice/{token}')

    # Scan the service package to attach any decorated views.
    config.scan(views)

    return config.make_wsgi_app()
