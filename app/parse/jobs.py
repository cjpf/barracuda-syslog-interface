import re
import json
from pygtail import Pygtail
from app import db, create_app
from app.models import Message, Recipient, Attachment, Account, Domain
import config


def parse_log():
    '''
    Parses ESS Log Data to store for the App
    '''
    app = create_app(config.JobConfig)
    app_context = app.app_context()
    app_context.push()

    with app.app_context():
        for line in Pygtail(app.config['ESS_LOG'], paranoid=True):
            data = re.findall(r'\{.*\}', line)
            data = json.loads(data[0])

            if _is_connection_test(data['account_id'], data['domain_id']):
                continue

            _store_account(app.logger, data)
            _store_domain(app.logger, data)
            _store_message(app.logger, data)
            if data['recipients']:
                for recipient in data['recipients']:
                    _store_recipient(
                        app.logger,
                        recipient,
                        data['message_id'])

            if data['attachments']:
                for attachment in data['attachments']:
                    _store_attachment(
                        app.logger,
                        attachment,
                        data['message_id'])

            db.session.commit()

    app.logger.info('Closing app context for parse_log()')
    app_context.pop()


def _add(logger, item):
    try:
        db.session.add(item)
        return True
    except Exception as e:
        db.session.rollback()
        logger.info(e)
        return False


def _store_message(logger, data):
    'Creates new Message entry if not already created.'
    logger.info("Checking for existing Message ID...({})".format(
        data['message_id']))
    if not _message_exists(data['message_id']):
        logger.info("Message ID not found. Creating entry.")
        m = Message(
            message_id=data['message_id'],
            account_id=data['account_id'],
            domain_id=data['domain_id'],
            src_ip=data['src_ip'],
            ptr_record=data['ptr_record'],
            hdr_from=data['hdr_from'],
            env_from=data['env_from'],
            hdr_to=data['hdr_to'],
            dst_domain=data['dst_domain'],
            size=data['size'],
            subject=data['subject'],
            timestamp=data['timestamp']
        )
        return _add(logger, m)


def _message_exists(message_id):
    'Checks to see if a Message already exists in the database.'
    return True if Message.query.filter_by(message_id=message_id).first() \
        else False


def _store_recipient(logger, data, message_id):
    'Creates new Recipient entry if Message has already been created'
    logger.info(
        'Checking for existing Message ID...({})'.format(message_id))
    if _message_exists(message_id):
        logger.info("Message ID found. Creating recipient entry.")
        r = Recipient(
            message_id=message_id,
            action=data['action'],
            reason=data['reason'],
            reason_extra=data['reason_extra'],
            delivered=data['delivered'],
            delivery_detail=data['delivery_detail'],
            email=data['email'],
        )
        return _add(logger, r)


def _store_attachment(logger, data, message_id):
    'Creates new Attachment entry if Message has already been created'
    logger.info(
        'Checking for existing Message ID...({})'.format(message_id))
    if _message_exists(message_id):
        logger.info("Message ID found. Creating attachment entry.")
        a = Attachment(
            message_id=message_id,
            name=data['name']
        )
        return _add(logger, a)


def _store_account(logger, data):
    'Creates new Account entry if not already created.'
    logger.info(
        "Checking for existing Account ID...({})".format(data['account_id']))
    if not _account_exists(data['account_id']):
        logger.info("Account ID not found. Creating entry.")
        a = Account(account_id=data['account_id'])
        return _add(logger, a)


def _account_exists(account_id):
    'Checks to see if an Account already exists in the database.'
    return True if Account.query.filter_by(account_id=account_id).first() \
        else False


def _store_domain(logger, data):
    'Creates new Domain entry if not already created.'
    logger.info(
        "Checking for existing Domain ID...({})".format(data['domain_id']))
    if not _domain_exists(data['domain_id']):
        logger.info("Domain ID not found. Creating entry.")
        d = Domain(domain_id=data['domain_id'])
        return _add(logger, d)


def _domain_exists(domain_id):
    'Checks to see if a Domain already exists in the database.'
    return True if Domain.query.filter_by(domain_id=domain_id).first() \
        else False


def _is_connection_test(account_id, domain_id):
    '''
    Checks to see if account id and domain id fields are empty.
    If empty, the log entry is simply a
    connection test from the service.
    '''
    if not account_id and not domain_id:
        return True
    return False
