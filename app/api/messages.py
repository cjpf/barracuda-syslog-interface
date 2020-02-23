from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from app.models import Message
from flask import jsonify, request, url_for


@bp.route('/messages/<string:message_id>', methods=['GET'])
@token_auth.login_required
def get_message(message_id):
    '''
    Retrieve a single Message
    '''
    return jsonify(Message.query.get_or_404(message_id).to_dict())


@bp.route('/messages', methods=['GET'])
@token_auth.login_required
def get_messages():
    '''
    Retrieve a collection of all Messages
    '''
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Message.to_collection_dict(
        Message.query, page, per_page, 'api.get_messages')
    return jsonify(data)


@bp.route('/messages', methods=['POST'])
@token_auth.login_required
def create_message():
    '''
    Create new Message
    '''
    data = request.get_json or {}
    if 'message_id' not in data:
        return bad_request('must include message_id')
    if Message.query.filter_by(message_id=data['message_id']).first():
        return bad_request('message_id already exists')
    message = Message()
    message.from_dict(data)
    db.session.add(message)
    db.session.commit()
    response = jsonify(message.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for(
        'api.get_message', message_id=message.message_id)
    return response


# @bp.route('/messages/<string:message_id>', methods=['PUT'])
# @token_auth.login_required
# def update_message(message_id):
#     pass


# @bp.route('/messages/<string:message_id>', methods=['DELETE'])
# @token_auth.login_required
# def delete_message(message_id):
#     pass
