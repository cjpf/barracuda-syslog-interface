import re
import json
import io
import config
import os
from pygtail import Pygtail
from app import db, create_app
from app.models import Message, Recipient, Attachment, Account, Domain


def parse_log():
    '''
    Parses ESS Log Data to store for the App
    '''
    app = create_app(config.JobConfig)
    app_context = app.app_context()
    app_context.push()

    _detect_rotated_log(app)

    with app.app_context():
        for line in Pygtail(app.config['ESS_LOG'],
                            paranoid=True,
                            full_lines=True):
            data = re.findall(r'\{.*\}', line)
            data = json.loads(data[0])

            if _is_connection_test(data['account_id'], data['domain_id']):
                app.logger.info('Conncetion Test Detected. Skipping...')
                continue

            if _message_exists(app.logger, data['message_id']):
                app.logger.info('Message ID FOUND. Skipping...')
                continue
            app.logger.info('Message ID NOT FOUND. Processing...')

            try:
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

            except Exception as e:
                db.session.rollback()
                app.logger.error(
                    "Failed to Process Message ({})".format(
                        data['message_id']))
                app.logger.error(e)
            else:
                db.session.commit()

    app.logger.info('Closing app context for parse_log')
    app_context.pop()


def _detect_rotated_log(app):
    '''
    Check inode stored in pygtail offset file and compare to inode of
    log file to detect rotations.
    if inode is different, delete offset file to reset
    '''
    try:
        with io.open(app.config['ESS_LOG_OFFSET']) as f:
            log_inode = re.findall(r'\d+', f.readline())
            log_inode = json.loads(log_inode[0])
            real_inode = os.stat(app.config['ESS_LOG']).st_ino
            if real_inode != log_inode:
                app.logger.info(
                    'inode value mismatch. Resetting pygtail offset file.')
                os.remove(app.config['ESS_LOG_OFFSET'])
    except Exception:
        app.logger.info('pygtail offset file not found')
        return


def _is_connection_test(account_id, domain_id):
    '''
    Checks to see if account id and domain id fields are empty.
    If empty, the log entry is simply a
    connection test from the service.
    '''
    if not account_id and not domain_id:
        return True
    return False


def _add(item):
    'Add an item to the db'
    try:
        db.session.add(item)
        return True
    except Exception as e:
        raise Exception(e)


def _store_account(logger, data):
    'Creates new Account entry if not already created.'
    if _account_exists(logger, data['account_id']):
        logger.info("Account ID FOUND. Skipping Account...")
        return False
    else:
        logger.info("Account ID NOT FOUND. Creating Account.")
        a = Account(account_id=data['account_id'])
        try:
            _add(a)
        except Exception as e:
            raise Exception(e)


def _store_attachment(logger, data, message_id):
    'Creates new Attachment entry if Message has already been created'
    logger.info('Creating Attachment.')
    a = Attachment(
        message_id=message_id,
        name=data['name']
    )
    try:
        _add(a)
    except Exception as e:
        raise Exception(e)


def _store_domain(logger, data):
    'Creates new Domain entry if not already created.'
    if _domain_exists(logger, data['domain_id']):
        logger.info("Domain ID FOUND. Skipping Domain...")
        return False
    else:
        logger.info("Domain ID NOT FOUND. Creating Domain.")
        d = Domain(domain_id=data['domain_id'], account_id=data['account_id'])
        try:
            _add(d)
        except Exception as e:
            raise Exception(e)


def _store_message(logger, data):
    'Creates new Message entry if not already created.'
    logger.info("Creating Message.")
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
    try:
        _add(m)
    except Exception as e:
        raise Exception(e)


def _store_recipient(logger, data, message_id):
    'Creates new Recipient entry if Message has already been created'
    logger.info('Creating Recipient.')
    r = Recipient(
        message_id=message_id,
        action=data['action'],
        reason=data['reason'],
        reason_extra=data['reason_extra'],
        delivered=data['delivered'],
        delivery_detail=data['delivery_detail'],
        email=data['email'],
    )
    try:
        _add(r)
    except Exception as e:
        raise Exception(e)


def _account_exists(logger, account_id):
    'Checks to see if an Account already exists in the database.'
    logger.info(
        "Checking for existing Account ID ({})".format(account_id))
    return True if Account.query.filter_by(account_id=account_id).first() \
        else False


def _domain_exists(logger, domain_id):
    'Checks to see if a Domain already exists in the database.'
    logger.info(
        "Checking for existing Domain ID ({})".format(domain_id))
    return True if Domain.query.filter_by(domain_id=domain_id).first() \
        else False


def _message_exists(logger, message_id):
    'Checks to see if a Message already exists in the database.'
    logger.info(
        'Checking for existing Message ID ({})'.format(message_id))
    return True if Message.query.filter_by(message_id=message_id).first() \
        else False
