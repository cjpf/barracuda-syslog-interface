from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from app.models import Account
from flask import jsonify, request, url_for


@bp.route('/accounts/<string:account_id>', methods=['GET'])
@token_auth.login_required
def get_account(account_id):
    '''
    Retrieve a single Account
    '''
    return jsonify(Account.query.get_or_404(account_id).to_dict())


@bp.route('/accounts', methods=['GET'])
@token_auth.login_required
def get_accounts():
    '''
    Retrieve a collection of all Accounts
    '''
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Account.to_collection_dict(
        Account.query, page, per_page, 'api.get_accounts')
    return jsonify(data)


@bp.route('/accounts', methods=['POST'])
@token_auth.login_required
def create_account():
    '''
    Create new Account
    '''
    data = request.get_json() or {}
    if 'account_id' not in data:
        return bad_request('must include account_id')
    if Account.query.filter_by(account_id=data['account_id']).first():
        return bad_request('account_id already exists')
    account = Account()
    account.from_dict(data)
    db.session.add(account)
    db.session.commit()
    response = jsonify(account.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for(
        'api.get_account', account_id=account.account_id)
    return response


@bp.route('/accounts/<string:account_id>', methods=['PUT'])
@token_auth.login_required
def update_account(account_id):
    '''
    Modify a Account
    '''
    account = Account.query.get_or_404(account_id)
    data = request.get_json() or {}
    if 'name' in data and data['name'] != account.name and \
            Account.query.filter_by(name=data['name']).first():
        return bad_request('account name already exists')
    account.from_dict(data)
    db.session.commit()
    return jsonify(account.to_dict())


@bp.route('/accounts/<string:account_id>', methods=['DELETE'])
@token_auth.login_required
def delete_account(account_id):
    '''
    Remove a Account
    Returns a representation of the deleted item
    '''
    account = Account.query.get_or_404(account_id)
    db.session.delete(account)
    db.session.commit()
    return jsonify(account.to_dict())
