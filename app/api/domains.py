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
    data = Domain.to_collection_dict(
        Domain.query, page, per_page, 'api.get_domains')
    return jsonify(data)


@bp.route('/domains', methods=['POST'])
@token_auth.login_required
def create_domain():
    '''
    Create new Domain
    '''
    data = request.get_json() or {}
    if 'domain_id' not in data and 'account_id' not in data:
        return bad_request('must include domain_id and account_id')
    if Domain.query.filter_by(domain_id=data['domain_id']).first():
        return bad_request('domain_id already exists')
    domain = Domain()
    domain.from_dict(data)
    db.session.add(domain)
    db.session.commit()
    response = jsonify(domain.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for(
        'api.get_domain', domain_id=domain.domain_id)
    return response


@bp.route('/domains/<int:domain_id>', methods=['PUT'])
@token_auth.login_required
def update_domain(domain_id):
    '''
    Modify a Domain
    '''
    domain = Domain.query.get_or_404(domain_id)
    data = request.get_json() or {}
    if 'name' in data and data['name'] != domain.name and \
            Domain.query.filter_by(name=data['name']).first():
        return bad_request('domain name already exists')
    domain.from_dict(data)
    db.session.commit()
    return jsonify(domain.to_dict())


@bp.route('/domains/<int:domain_id>', methods=['DELETE'])
@token_auth.login_required
def delete_domain(domain_id):
    '''
    Remove a Domain
    Returns a representation of the deleted item
    '''
    domain = Domain.query.get_or_404(domain_id)
    db.session.delete(domain)
    db.session.commit()
    return jsonify(domain.to_dict())
