from http import HTTPStatus

from flask import request

from urlshortener import exceptions
from urlshortener import storage
from urlshortener.flask import app, api_success, api_failure


@app.route('/api/', methods=['GET'])
def list():
    return api_success(HTTPStatus.OK, storage.list())


@app.route('/api/', methods=['POST'])
def create():
    url = request.form.get('url')
    if not url:
        return api_failure(HTTPStatus.BAD_REQUEST, 'missing url')
    try:
        entity = storage.create(url)
    except exceptions.AlreadyExists:
        return api_failure(HTTPStatus.CONFLICT,
                           'url already exists')
    except exceptions.NoAvailableIDs:
        return api_failure(HTTPStatus.SERVICE_UNAVAILABLE,
                           'unable to find unused ID')
    else:
        return api_success(HTTPStatus.CREATED, entity)


@app.route('/api/<url_id>', methods=['GET'])
def retrieve(url_id):
    try:
        entity = storage.retrieve(url_id)
    except exceptions.NotFound:
        return api_failure(HTTPStatus.NOT_FOUND, 'not found')
    else:
        return api_success(HTTPStatus.OK, entity)


@app.route('/api/<url_id>', methods=['PUT'])
def update(url_id):
    url = request.form.get('url')
    if not url:
        return api_failure(HTTPStatus.BAD_REQUEST, 'missing url')
    try:
        entity = storage.update(url_id, url)
    except exceptions.NotFound:
        return api_failure(HTTPStatus.NOT_FOUND, 'not found')
    else:
        return api_success(HTTPStatus.OK, entity)


@app.route('/api/<url_id>', methods=['DELETE'])
def delete(url_id):
    try:
        storage.delete(url_id)
    except exceptions.NotFound:
        return api_failure(HTTPStatus.NOT_FOUND, 'not found')
    else:
        return api_success(HTTPStatus.NO_CONTENT, None)
