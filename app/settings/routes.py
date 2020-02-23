import requests
from datetime import datetime
from flask import render_template, request, flash, redirect, url_for,\
    current_app
from flask_login import login_required, current_user
from app import db
from app.settings import bp
from app.settings.forms import SetDomainForm
from app.models import Domain, Message


BASE_URL = "http://localhost:5000"


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
    url = '{}{}'.format(BASE_URL, url_for('api.get_domains'))
    headers = {
        'Authorization': 'Bearer {}'.format(current_user.token)
    }
    print(headers)
    response = requests.get(url, headers=headers)
    if (response.status_code != 200):
        return 'Error'  # TODO Redirect to some Error HTML page
    domains = response.json()['items']
    unnamed_domains = _get_unnamed_domains(domains)
    guesses = _calculate_guess(unnamed_domains)
    return render_template('settings/settings.html',
                           title='Settings',
                           domains=domains,
                           guesses=guesses)


def _get_unnamed_domains(domains):
    '''
    Takes a dict of domains
    Returns a list of domains with no name
    '''
    unknown_domains = []
    for domain in domains:
        if domain['name'] is None:
            unknown_domains.append(domain['domain_id'])
    return unknown_domains


def _calculate_guess(domains):
    '''
    Returns list of all guesses for unnamed domains
    '''
    destinations = {}
    guesses = {}
    for domain in domains:
        messages = Message.query.filter_by(domain_id=domain).all()
        for message in messages:
            if message.dst_domain in destinations:
                destinations[message.dst_domain] += 1
            else:
                destinations[message.dst_domain] = 1
        max = 0
        guess = 'None'
        for d in destinations.items():
            if d[1] > max:
                max = d[1]
                guess = d[0]
        # if len(guess) > 0:
        current_app.logger.info(
            'The best guess for domain name to associate with {} is {}'
            .format(domain, guess))
        guesses[domain] = guess
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
