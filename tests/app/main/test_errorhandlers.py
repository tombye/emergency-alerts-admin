import pytest
from bs4 import BeautifulSoup
from flask import Response, url_for
from flask_wtf.csrf import CSRFError
from notifications_python_client.errors import HTTPError
from notifications_utils.recipients import CSVTooBigError


def test_bad_url_returns_page_not_found(client):
    response = client.get('/bad_url')
    assert response.status_code == 404
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert page.h1.string.strip() == 'Page not found'
    assert page.title.string.strip() == 'Page not found – GOV.UK Notify'


def test_load_service_before_request_handles_404(client_request, mocker):
    exc = HTTPError(Response(status=404), 'Not found')
    get_service = mocker.patch('app.service_api_client.get_service', side_effect=exc)

    client_request.get(
        'main.service_dashboard',
        service_id='00000000-0000-0000-0000-000000000000',
        _expected_status=404
    )

    get_service.assert_called_once_with('00000000-0000-0000-0000-000000000000')


@pytest.mark.parametrize('url', [
    '/new-password/MALFORMED_TOKEN',
    '/user-profile/email/confirm/MALFORMED_TOKEN',
    '/verify-email/MALFORMED_TOKEN'
])
def test_malformed_token_returns_page_not_found(logged_in_client, url):
    response = logged_in_client.get(url)

    assert response.status_code == 404
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert page.h1.string.strip() == 'Page not found'
    flash_banner = page.find('div', class_='banner-dangerous').string.strip()
    assert flash_banner == "There’s something wrong with the link you’ve used."
    assert page.title.string.strip() == 'Page not found – GOV.UK Notify'


def test_csrf_returns_400(logged_in_client, mocker):
    # we turn off CSRF handling for tests, so fake a CSRF response here.
    csrf_err = CSRFError('400 Bad Request: The CSRF tokens do not match.')
    mocker.patch('app.main.views.index.render_template', side_effect=csrf_err)

    response = logged_in_client.get('/cookies')

    assert response.status_code == 400
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert page.h1.string.strip() == 'Sorry, there’s a problem with GOV.UK Notify'
    assert page.title.string.strip() == 'Sorry, there’s a problem with the service – GOV.UK Notify'


def test_csrf_redirects_to_sign_in_page_if_not_signed_in(client, mocker):
    csrf_err = CSRFError('400 Bad Request: The CSRF tokens do not match.')
    mocker.patch('app.main.views.index.render_template', side_effect=csrf_err)

    response = client.get('/cookies')

    assert response.status_code == 302
    assert response.location == url_for('main.sign_in', next='/cookies', _external=True)


def test_405_returns_something_went_wrong_page(client, mocker):
    response = client.post('/')

    assert response.status_code == 405
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert page.h1.string.strip() == 'Sorry, there’s a problem with GOV.UK Notify'
    assert page.title.string.strip() == 'Sorry, there’s a problem with the service – GOV.UK Notify'


def test_csv_too_big_returns_413(client, mocker):
    csv_error = CSVTooBigError()
    # a more realistic view would be "send.check_messages", but using one that
    # doesn't require lots of params is sufficient for this test.
    mocker.patch('app.main.views.index.render_template', side_effect=csv_error)
    response = client.get('/cookies')

    assert response.status_code == 413
    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')
    assert page.h1.string.strip() == 'The file you uploaded was too big'
