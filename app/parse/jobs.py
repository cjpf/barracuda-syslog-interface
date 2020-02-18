from pygtail import Pygtail
import sys
import re
import json
from app.models import Message, Account, Domain
from app import db



def hello_job():
    print('Hello Job!')


def parse_log():
    for line in Pygtail("ess.log"):
        data = re.findall(r'\{.*\}', line)
        data = json.loads(data[0])
        id = data['message_id']
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

        #check if account id exists in acct table
        #   if not, add new acct to acct table
        if not Account.query.filter_by(id=account_id).first():
            a = Account(id=account_id)
            db.session.add(a)

        if not Domain.query.filter_by(id=domain_id).first():
            d = Domain(id=domain_id)
            db.session.add(d)

        if not Message.query.filter_by(id=id).first():
            m = Message(id=id, account_id=account_id, domain_id=domain_id,
                        src_ip=src_ip, ptr_record=ptr_record, hdr_from=hdr_from,
                        env_from=env_from, hdr_to=hdr_to, dst_domain=dst_domain,
                        size=size, subject=subject, timestamp=timestamp)
            db.session.add(m)
        db.session.commit()
    