from app.api import bp
from flask import jsonify, request
from app.models import User

@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    '''
    Retrieve a single User 
    '''
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)
    pass


@bp.route('/users', methods=['POST'])
def create_user():
    pass


@bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    pass


@bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    pass
