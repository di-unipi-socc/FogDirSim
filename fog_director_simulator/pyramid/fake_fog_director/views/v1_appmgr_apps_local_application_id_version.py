from pyramid.request import Request
from pyramid.view import view_config


@view_config(
    route_name='api.v1.appmgr.apps.local_application_id.version',
    renderer='json',  # Needed due to https://github.com/striglia/pyramid_swagger/issues/236
)
def v1_appmgr_apps_local_application_id_version(request: Request) -> None:
    request.database_logic.delete_application(
        localAppId=request.swagger_data['local_application_id'],
        version=request.swagger_data['version'],
    )
