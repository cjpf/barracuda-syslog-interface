from datetime import datetime
from flask import render_template, jsonify, url_for
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import Message


@bp.before_request
def before_request():
    'Process before each request'
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    'Home Page featuring Email Statistics Graphs'
    return render_template('index.html', title='Dashboard')


@bp.route('/messages')
@bp.route('/messages/<int:page>')
def messages(page=1):
    messages = Message.query.order_by(
        Message.timestamp.desc()).paginate(page, 15, False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html',
                           messages=messages.items,
                           next_url=next_url,
                           prev_url=prev_url)
