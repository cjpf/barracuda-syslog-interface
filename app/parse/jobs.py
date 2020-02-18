import re
import json
from pygtail import Pygtail
from app import db
from app.models import Message, Account, Domain


def hello_job():
    print('Hello Job!')


def parse_log():
    '''
    Parses ESS Log Data to store for the App
    '''
    for line in Pygtail("ess.log", paranoid=True):
        data = re.findall(r'\{.*\}', line)
        data = json.loads(data[0])

        if _is_connection_test(data['account_id'], data['domain_id']):
            continue

        _store_account(data)
        _store_domain(data)
        _store_message(data)
        db.session.commit()


def _store_message(data):
    'Creates new Message entry if not already created.'
    print("Checking for existing Message ID...({})".format(data['message_id']))
    if not _message_exists(data['message_id']):
        print("Message ID not found. Creating entry.")
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
            db.session.add(m)
        except Exception as e:
            db.rollback()
            print(e)  # TODO log exception


def _message_exists(message_id):
    'Checks to see if a Message already exists in the database.'
    return True if Message.query.filter_by(message_id=message_id).first() \
        else False


def _store_account(data):
    'Creates new Account entry if not already created.'
    print("Checking for existing Account ID...({})".format(data['account_id']))
    if not _account_exists(data['account_id']):
        print("Account ID not found. Creating entry.")
        a = Account(account_id=data['account_id'])
        try:
            db.session.add(a)
        except Exception as e:
            db.rollback()
            print(e)  # TODO log exception


def _account_exists(account_id):
    'Checks to see if an Account already exists in the database.'
    return True if Account.query.filter_by(account_id=account_id).first() \
        else False


def _store_domain(data):
    'Creates new Domain entry if not already created.'
    print("Checking for existing Domain ID...({})".format(data['domain_id']))
    if not _domain_exists(data['domain_id']):
        print("Domain ID not found. Creating entry.")
        d = Domain(domain_id=data['domain_id'])
        try:
            db.session.add(d)
        except Exception as e:
            db.rollback()
            print(e)  # TODO log exception


def _domain_exists(domain_id):
    'Checks to see if a Domain already exists in the database.'
    return True if Domain.query.filter_by(domain_id=domain_id).first() \
        else False


def _is_connection_test(account_id, domain_id):
    '''
    This function checks to see if account id field is empty.
    If this field is empty, the log entry is simply a
    connection test from the service.
    '''
    if not account_id and not domain_id:
        return True
    return False
