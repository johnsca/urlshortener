from http import HTTPStatus

from flask import send_from_directory

from urlshortener import exceptions, storage
from urlshortener.flask import app


@app.route('/', methods=['GET'])
def index(file_path=None):
    return send_from_directory('static', 'index.html')


@app.route('/<url_id>', methods=['GET'])
def view(url_id):
    try:
        entity = storage.view(url_id)
    except exceptions.NotFound:
        return 'not found', int(HTTPStatus.NOT_FOUND)
    else:
        return entity['url'], int(HTTPStatus.FOUND), {
            'Location': entity['url'],
        }
