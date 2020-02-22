from flask import g, jsonify
from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth


@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    '''
    Gets the user's token from the database.
    Because the User.get_token function either returns
    existing token OR generates new token, we write it back
    into the database each time so that we know it is always
    saved.
    '''
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})


@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    '''
    Revokes the current user's token and returns No Content
    '''
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204  # No Content
