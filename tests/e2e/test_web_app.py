import pytest

from flask import session

def test_register(client):
    response_code = client.get('/register').status_code
    assert response_code == 200

    response = client.post(
        '/register',
        data={'user_name': 'Michael', 'password': 'CarelessWhisper1984'}
    )
    assert response.headers['Location'] == 'http://localhost/login'


def test_login(client, auth):
    status_code = client.get('/login').status_code
    assert status_code == 200

    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_name'] == 'thorke'


def test_logout(client, auth):
    auth.login()
    with client:
        auth.logout()
        assert 'user_id' not in session


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200


def test_register_validation(client):
    response = client.post(
        '/register',
        data={'user_name': '', 'password': ''}
    )
    assert b'Your user name is required' in response.data


def test_login_failure(client, auth):
    response = client.post(
        '/login',
        data={'user_name': 'nonexistent', 'password': 'wrongpassword'}
    )
    assert b'Invalid username or password' in response.data


def test_protected_route_requires_login(client):
    response = client.get('/profile', follow_redirects=True)
    assert b'Please log in to access this page' in response.data
    assert response.request.path == '/login'


def test_browse_page_content(client):
    response = client.get('/browse')
    assert response.status_code == 200
    assert b'Recipes' in response.data