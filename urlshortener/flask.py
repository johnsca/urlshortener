from flask import Flask
from flask.json import jsonify

app = Flask(__name__)


def api_success(status_code, result):
    response = jsonify(success=True, result=result)
    response.status_code = int(status_code)
    return response


def api_failure(status_code, message):
    response = jsonify(success=False, error=message)
    response.status_code = int(status_code)
    return response
