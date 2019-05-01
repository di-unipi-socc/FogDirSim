import tarfile
from typing import Any
from typing import Dict

import yaml
from pyramid.httpexceptions import HTTPConflict
from pyramid.request import Request
from pyramid.view import view_config

from fog_director_simulator.database.models import Application
from fog_director_simulator.database.models import ApplicationProfile
from fog_director_simulator.pyramid.fake_fog_director.formatters import application_format


def _extract_package_yaml_from_archive(fileobj: Any) -> Dict[str, Any]:
    # NOTE: This deals only with tar.gz archives
    tar = tarfile.open(mode="r:gz", fileobj=fileobj)
    package_yaml_file = tar.extractfile('package.yaml')
    return yaml.safe_load(package_yaml_file)  # type: ignore


@view_config(route_name='api.v1.appmgr.localapps.upload', request_method='POST')
def post_v1_appmgr_localapps_upload(request: Request) -> Dict[str, Any]:
    # TODO: make sure that we support tar file as well
    package_metadata = _extract_package_yaml_from_archive(request.swagger_data['file'])
    info = package_metadata['info']
    app = package_metadata['app']

    if request.database_logic.get_application_by_name(name=info['name']):
        raise HTTPConflict

    application = Application(
        localAppId=info['name'],  # This is an internal detail meant to simplify things (we don't know how CISCO creates it)
        version=info['version'],
        name=info['name'],
        description=info['description'],
        isPublished=True if request.swagger_data['X-Publish-On-Upload'] else False,
        profileNeeded=ApplicationProfile.from_iox_name(app['resources']['profile']),
        # WARNING: This could fail badly in case of a custom application profile
    )
    formatted_application = application_format(application)
    request.database_logic.create(application)

    return formatted_application
