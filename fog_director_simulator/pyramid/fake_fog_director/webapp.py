import os
from functools import lru_cache

import pyramid_swagger
from pyramid.config import Configurator
from pyramid.router import Router
from pyramid_swagger.renderer import PyramidSwaggerRendererFactory

from fog_director_simulator.pyramid.fake_fog_director import views


@lru_cache(maxsize=1)
def create_application() -> Router:
    """Create the WSGI application, post-fork."""
    config = Configurator()

    config.add_settings({
        'pyramid_swagger.swagger_versions': ['2.0'],
        'pyramid_swagger.enable_response_validation': True,
        'pyramid_swagger.enable_swagger_spec_validation': True,
        # Disable path validation so that simulator_api can handle 404s
        'pyramid_swagger.enable_path_validation': False,
        'pyramid_swagger.schema_directory': os.path.join('api_docs', 'fog_director_api'),
        'pyramid_swagger.schema_file': 'swagger.yaml',
        'pyramid_swagger.base_path_api_docs': 'api/',
        'pyramid_swagger.skip_validation': [
            '/(static)\\b',
            '/api/(status)\\b',
            '/api/(swagger.json)\\b',
            '/api/(swagger.yaml)\\b',
        ],

        # Ensure that swagger.json endpoint retrieves the whole spec
        'pyramid_swagger.dereference_served_schema': True,
        # Remove spec references to speed up (a bit) request and response validation
        'bravado_core.internally_dereference_refs': True,
    })

    config.include(pyramid_swagger)

    # Set the default renderer to our JSON renderer
    config.add_renderer(None, PyramidSwaggerRendererFactory())

    # Add status metrics view with the internal_ip_only predicate
    config.add_route('api.status', '/api/status')

    # Scan the service package to attach any decorated views.
    config.scan(views)

    return config.make_wsgi_app()
