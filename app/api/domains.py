from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from app.models import Domain
from flask import jsonify, request, url_for


@bp.route('/domains/<int:domain_id>', methods=['GET'])
@token_auth.login_required
def get_domain(domain_id):
    '''
    Retrieve a single Domain
    '''
    return jsonify(Domain.query.get_or_404(domain_id).to_dict())


@bp.route('/domains', methods=['GET'])
@token_auth.login_required
def get_domains():
    '''
    Retrieve a collection of all Domains
    '''
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Domain.to_collection_dict(Domain.query, page, per_page, 'api.get_domains')
    return jsonify(data)


@bp.route('/domains', methods=['POST'])
@token_auth.login_required
def create_domain():
    pass


@bp.route('/domains/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_domain(id):
    pass


@bp.route('/domains/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_domain(id):
    pass
