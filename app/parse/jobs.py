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
        message_id = data['message_id']
        account_id = data['account_id']
        domain_id = data['domain_id']
        src_ip = data['src_ip']
        ptr_record = data['ptr_record']
        hdr_from = data['hdr_from']
        env_from = data['env_from']
        hdr_to = data['hdr_to']
        dst_domain = data['dst_domain']
        size = data['size']
        subject = data['subject']
        timestamp = data['timestamp']

        if _is_test_entry(account_id, domain_id):
            continue

        print("Checking for existing Account ID...({})".format(account_id))
        if not Account.query.filter_by(account_id=account_id).first():
            print("Account ID not found. Creating entry.")
            a = Account(account_id=account_id)
            db.session.add(a)

        print("Checking for existing Domain ID...({})".format(domain_id))
        if not Domain.query.filter_by(domain_id=domain_id).first():
            print("Domain ID not found. Creating entry.")
            d = Domain(domain_id=domain_id)
            db.session.add(d)

        print("Checking for existing Message ID...({})".format(message_id))
        if not Message.query.filter_by(message_id=message_id).first():
            print("Message ID not found. Creating entry.")
            m = Message(
                message_id=message_id,
                account_id=account_id,
                domain_id=domain_id,
                src_ip=src_ip,
                ptr_record=ptr_record,
                hdr_from=hdr_from,
                env_from=env_from,
                hdr_to=hdr_to,
                dst_domain=dst_domain,
                size=size,
                subject=subject,
                timestamp=timestamp
            )
            db.session.add(m)
        db.session.commit()
def _store_account(data):
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
    return True if Account.query.filter_by(account_id=account_id).first() \
        else False


def _is_test_entry(account_id, domain_id):
    '''
    This function checks to see if account id field is empty.
    If this field is empty, the log entry is simply a 
    connection test from the service.
    '''
    if not account_id and not domain_id:
        return True
    return False
