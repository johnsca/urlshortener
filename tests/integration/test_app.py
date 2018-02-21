# Integration tests for the app as a whole.
#
# Integration tests should confirm the correct behavior of the application
# along with all of its external dependencies.  These are the slowest of tests
# and thus should be used somewhat sparingly, but they are very important to
# confirm the application as a whole works as expected.
#
# Integration tests are often done with things like Selenium or BDD frameworks
# run against a live staging environment.
import time
from multiprocessing import Process
from unittest.mock import ANY
from urllib.parse import urljoin

import pytest
import requests  # this makes actual HTTP requests to the server

from urlshortener import app


@pytest.fixture(scope='module')
def server_url():
    server_url = 'http://127.0.0.1:5000/api/'
    server_proc = Process(target=app.run)
    server_proc.start()
    try:
        for attempt in range(3):
            try:
                requests.get(server_url)
                break
            except requests.ConnectionError:
                time.sleep(1)
        else:
            pytest.fail('Unable to connect to test server')
        yield server_url
    finally:
        server_proc.terminate()


def test_app_failures(server_url):
    entity_url = urljoin(server_url, 'foo')

    response = requests.get(entity_url)
    assert response.status_code == 404
    assert response.json()['success'] is False

    response = requests.put(entity_url)
    assert response.status_code == 400
    assert response.json()['success'] is False

    response = requests.put(entity_url, data={'url': 'invalid'})
    assert response.status_code == 404
    assert response.json()['success'] is False

    response = requests.delete(entity_url)
    assert response.status_code == 404
    assert response.json()['success'] is False

    response = requests.post(server_url, data={})
    assert response.status_code == 400
    assert response.json()['success'] is False


def test_api_success(server_url):
    # create new URL
    response = requests.post(server_url, data={'url': 'first'})
    assert response.status_code == 201
    assert response.json()['success'] is True
    assert response.json()['result'] == {
        'id': ANY,  # use magic mock value for ID that is always equal
        'url': 'first',
        'views': 0,
    }

    entity_id = response.json()['result']['id']
    entity_url = urljoin(server_url, entity_id)

    # retrieve it
    response = requests.get(entity_url)
    assert response.status_code == 200
    assert response.json()['result'] == {
        'id': entity_id,
        'url': 'first',
        'views': 0,
    }

    # update to new URL
    response = requests.put(entity_url, data={'url': 'second'})
    assert response.status_code == 200
    assert response.json()['result'] == {
        'id': entity_id,
        'url': 'second',
        'views': 0,
    }

    # list all
    response = requests.get(server_url)
    assert response.status_code == 200
    assert response.json()['result'] == [{
        'id': entity_id,
        'url': 'second',
        'views': 0,
    }]

    # delete it
    response = requests.delete(entity_url)
    assert response.status_code == 204

    # fail to retrieve it after deletion
    response = requests.get(entity_url)
    assert response.status_code == 404
