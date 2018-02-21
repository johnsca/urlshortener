# Unit tests for the API handlers.
#
# Unit tests should cover all branches of the unit under test and should
# provide all dependencies, through mocking, dependency injection, etc,
# so that the test is only covering the unit under test.
#
# The unit tests will necessarily be tightly coupled to the code and
# will have to be updated any time the code is modified.  They will also
# obviously not be able to test the interaction between components.  However,
# they are much faster, more reliable, and easier to provide 100% coverage
# than other forms of tests (functional, integration).
from unittest.mock import patch, sentinel

import pytest

from urlshortener import api, exceptions


@pytest.fixture
def request():
    """
    Provide mock for request test arg.

    The request will be patched with a mock that has a `form` dict attribute.
    """
    patcher = patch.object(api, 'request')
    mock_request = patcher.start()
    mock_request.form = {}
    yield mock_request
    patcher.stop()


@pytest.fixture
def storage():
    """
    Provide mock for storage test arg.
    """
    patcher = patch.object(api, 'storage')
    yield patcher.start()
    patcher.stop()


@pytest.fixture
def api_success():
    """
    Provide mock for api_success test arg.

    Calls to api_success will always return the sentinel value and will
    set the status code and message on it for easy assertion.
    """
    def _mock(status_code, message):
        sentinel.api_success.status_code = status_code
        sentinel.api_success.message = message
        return sentinel.api_success

    patcher = patch.object(api, 'api_success', side_effect=_mock)
    patcher.start()
    yield sentinel.api_success
    patcher.stop()


@pytest.fixture
def api_failure():
    """
    Provide mock for api_failure test arg.

    Calls to api_failure will always return the sentinel value and will
    set the status code and message on it for easy assertion.
    """
    def _mock(status_code, message):
        sentinel.api_failure.status_code = status_code
        sentinel.api_failure.message = message
        return sentinel.api_failure

    patcher = patch.object(api, 'api_failure', side_effect=_mock)
    patcher.start()
    yield sentinel.api_failure
    patcher.stop()


def test_create(request, storage, api_success, api_failure):
    # no url
    assert api.create() is api_failure
    assert api_failure.status_code == 400

    # url and no storage error
    request.form['url'] = 'foo'
    assert api.create() is api_success
    assert api_success.status_code == 201
    storage.create.assert_called_once_with('foo')

    # already exists storage error
    storage.create.side_effect = exceptions.AlreadyExists
    assert api.create() is api_failure
    assert api_failure.status_code == 409

    # no available IDs storage error
    storage.create.side_effect = exceptions.NoAvailableIDs
    assert api.create() is api_failure
    assert api_failure.status_code == 503


def test_retrieve(storage, api_success, api_failure):
    # no errors
    assert api.retrieve('dummy_id') is api_success
    assert api_success.status_code == 200

    # not found error
    storage.retrieve.side_effect = exceptions.NotFound
    assert api.retrieve('dummy_id') is api_failure
    assert api_failure.status_code == 404


def test_update(request, storage, api_success, api_failure):
    # no url
    assert api.update('dummy_id') is api_failure
    assert api_failure.status_code == 400

    # url and no errors
    request.form['url'] = 'foo'
    assert api.update('dummy_id') is api_success
    assert api_success.status_code == 200
    storage.update.assert_called_once_with('dummy_id', 'foo')

    storage.update.side_effect = exceptions.NotFound
    assert api.update('dummy_id') is api_failure
    assert api_failure.status_code == 404


def test_delete(storage, api_success, api_failure):
    # no errors
    assert api.delete('dummy_id') is api_success
    assert api_success.status_code == 204

    # not found error
    storage.delete.side_effect = exceptions.NotFound
    assert api.delete('dummy_id') is api_failure
    assert api_failure.status_code == 404
