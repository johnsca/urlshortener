# Functional tests for the API handlers and storage backend.
#
# Functional tests should confirm the correct behavior of the application
# or library.  They are a middle ground between integration and unit tests;
# they can bring together various components of the code under test but
# should not have any dependencies on external resources or code.  They should
# not care about the implementation details of the code under test, just that
# it performs as expected.
from functools import partial
from unittest.mock import Mock, patch

import pytest

from urlshortener import api


@pytest.fixture
def request():
    """
    Provide mock for request test arg.

    The request will be patched with a mock that has a `form` dict attribute.
    It will also have a `form_values` context manager method that will
    temporarily patch values into the request form.
    """
    form = {}
    patcher = patch.object(api, 'request',
                           form=form,
                           form_values=partial(patch.dict, form))
    mock_request = patcher.start()
    yield mock_request
    patcher.stop()


@pytest.fixture
def uuids():
    """
    Fixture to provide `uuids` test parameter.

    Mocks out uuid.uuid4() to provide a predicable list of values,
    and provides a generator to the test over those values.
    """
    mock_uuids = ['one', 'two', 'three', 'four', 'five']
    patcher = patch('urlshortener.storage.uuid4',
                    side_effect=[Mock(hex=uuid) for uuid in mock_uuids])
    patcher.start()
    yield iter(mock_uuids)
    patcher.stop()


class MockResponse(dict):
    """
    Placeholder for a response object created by flask.jsonify.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_code = None


@patch('urlshortener.flask.jsonify', MockResponse)
def test_api_failures(request):
    response = api.retrieve('foo')
    assert response.status_code == 404
    assert response['success'] is False

    response = api.update('foo')
    assert response.status_code == 400
    assert response['success'] is False

    with request.form_values(url='invalid'):
        response = api.update('foo')
        assert response.status_code == 404
        assert response['success'] is False

    response = api.delete('foo')
    assert response.status_code == 404
    assert response['success'] is False

    response = api.create()
    assert response.status_code == 400
    assert response['success'] is False


@patch('urlshortener.flask.jsonify', MockResponse)
def test_api_success(request, uuids):
    # create new URL
    with request.form_values(url='first'):
        response = api.create()
        expected_id = next(uuids)
        assert response.status_code == 201
        assert response['success'] is True
        assert response['result'] == {
            'id': expected_id,
            'url': 'first',
            'views': 0,
        }

    # retrieve it
    response = api.retrieve(expected_id)
    assert response.status_code == 200
    assert response['result'] == {
        'id': expected_id,
        'url': 'first',
        'views': 0,
    }

    # update to new URL
    with request.form_values(url='second'):
        response = api.update(expected_id)
        assert response.status_code == 200
        assert response['result'] == {
            'id': expected_id,
            'url': 'second',
            'views': 0,
        }

    # delete it
    response = api.delete(expected_id)
    assert response.status_code == 204
    assert response['result'] is None

    # fail to retrieve it after deletion
    response = api.retrieve(expected_id)
    assert response.status_code == 404
