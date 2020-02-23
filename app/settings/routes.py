from datetime import datetime
from flask import render_template, request, flash, redirect, url_for,\
    current_app
from flask_login import login_required, current_user
from app import db
from app.settings import bp
from app.settings.forms import SetDomainForm
from app.models import Domain, Message


@bp.before_request
def before_request():
    'Process before each request'
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/settings', methods=['GET'])
@login_required
def settings():
    'Settings Page for App configuration'
    domains = Domain.query.all()
    guesses = _calculate_guess()
    return render_template('settings/settings.html',
                           title='Settings',
                           domains=domains,
                           guesses=guesses)


def _calculate_guess():
    '''
    Returns list of all guesses for unnamed domains
    '''
    domains = Domain.query.filter_by(name=None).all()
    destinations = {}
    guesses = {}
    for domain in domains:
        messages = Message.query.filter_by(domain_id=domain.domain_id).all()
        for message in messages:
            if message.dst_domain in destinations:
                destinations[message.dst_domain] += 1
            else:
                destinations[message.dst_domain] = 1
        max = 0
        for d in destinations.items():
            if d[1] > max:
                max = d[1]
                guess = d[0]
        current_app.logger.info(
            'The best guess for domain name to associate with {} is {}'
            .format(domain.domain_id, guess))
        guesses[domain.domain_id] = guess
    return guesses


@bp.route('/settings/set_domain/<domain_id>', methods=['GET', 'POST'])
@login_required
def set_domain(domain_id):
    form = SetDomainForm(domain_id)
    domain = Domain.query.filter_by(domain_id=domain_id).first()
    if form.validate_on_submit():
        domain.name = form.domain_name.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('settings.settings'))
    elif request.method == 'GET':
        form.domain_name.data = domain.name
    return render_template('settings/set_domain.html',
                           title='Set Domain',
                           form=form)
