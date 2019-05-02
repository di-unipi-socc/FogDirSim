import os
from functools import lru_cache

from pyramid.router import Router

from fog_director_simulator.pyramid import default_pyramid_configuration
from fog_director_simulator.pyramid.simulator_api import views


@lru_cache(maxsize=1)
def create_application() -> Router:
    """Create the WSGI application, post-fork."""
    config = default_pyramid_configuration(
        root_swagger_spec_path=os.path.join('api_docs', 'fog_director_api', 'swagger.yaml'),
        base_path_api_docs='/api/',
        database_verbose=False,
    )

    # Add status metrics view with the internal_ip_only predicate
    config.add_route('api.status', '/api/status')

    # Scan the service package to attach any decorated views.
    config.scan(views)

    return config.make_wsgi_app()