import typing
if typing.TYPE_CHECKING:
    from webtest import TestApp


def test_post_v1_appmgr_localapps_upload_without_tokens(testapp: 'TestApp') -> None:
    response = testapp.post('/api/v1/appmgr/localapps/upload', expect_errors=True)
    assert response.status_code == 400


def test_post_v1_appmgr_localapps_upload_without_application_archive(testapp: 'TestApp') -> None:
    response = testapp.post('/api/v1/appmgr/localapps/upload', expect_errors=True)
    assert response.status_code == 400


def test_post_v1_appmgr_localapps_upload_with_application_archive(testapp: 'TestApp') -> None:
    with open('fog_director_application_archives/NettestApp2V1_lxc.tar.gz', 'rb') as f:
        application_archive_content = f.read()

    response = testapp.post(
        '/api/v1/appmgr/localapps/upload',
        headers={
            'X-Token-Id': 'token',
        },
        upload_files=[
            ('file', 'file', application_archive_content),
        ],
    )
    assert response.status_code == 200
    assert response.json == {
        'cpuUsage': 200,
        'creationDate': -1,
        'localAppId': 'NettestApp2',
        'memoryUsage': 64,
        'profileNeeded': 'c1.small',
        'published': 'unpublished',
        'sourceAppName': 'NettestApp2:1',
        'version': '1',
    }
