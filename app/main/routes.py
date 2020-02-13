from datetime import datetime
from flask import render_template
from flask_login import login_required, current_user
from app import db
from app.main import bp


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    return render_template('index.html', title='Dashboard')
