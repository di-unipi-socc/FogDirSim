import typing
if typing.TYPE_CHECKING:
    from webtest import TestApp


def test_delete_v1_appmgr_tokenservice_token_without_tokens(testapp: 'TestApp') -> None:
    response = testapp.delete('/api/v1/appmgr/tokenservice/{token}', expect_errors=True)
    assert response.status_code == 400