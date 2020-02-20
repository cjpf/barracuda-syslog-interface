from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
'''
Error Representation:
{
    'error': 'short error description',
    'message': 'error message(optional)'
}
'''


def error_response(status_code, message=None):
    '''
    Generates an error response payload
    jsonify() returns a default 200 for the response
    because of this, we must set the response status_code manually
    '''
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(message):
    '''
    For when client sends invalid request
    '''
    return error_response(400, message)
