import unittest
import config
from app import create_app, db
from app.models import User, Message, Recipient, Attachment, Account, Domain


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config.TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_user(self):
        u = User(email='susan@test.com')
        db.session.add(u)
        db.session.commit()
        u = User.query.filter_by(email='susan@test.com').first()
        self.assertTrue(u)
        u = User.query.filter_by(email='fred@test.com').first()
        self.assertFalse(u)

    def test_password_hashing(self):
        u = User(email='susan@test.com')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))


class MessageModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config.TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_message(self):
        message_id = '1578083234-893239-2956-1311577-1'
        account_id = 'ESS101010'
        domain_id = '123456'
        src_ip = '23.229.13.132'
        ptr_record = 'li686-132.members.linode.com'
        hdr_from = 'CJ Pfenninger cjpf@charliejuliet.net'
        env_from = 'cjpf@charliejuliet.net'
        hdr_to = 'cjpf@sendthemail.com'
        dst_domain = 'sendthemail.com'
        size = 5350
        subject = "banned: 1231498134 from this"
        timestamp = "2020-01-03T20:27:18+0000"
        m = Message(message_id=message_id, account_id=account_id, domain_id=domain_id,
                    src_ip=src_ip, ptr_record=ptr_record, hdr_from=hdr_from,
                    env_from=env_from, hdr_to=hdr_to, dst_domain=dst_domain,
                    size=size, subject=subject, timestamp=timestamp)
        db.session.add(m)
        db.session.commit()
        m = Message.query.filter_by(
            message_id='1578083234-893239-2956-1311577-1').first()
        self.assertTrue(m)
        m = Message.query.filter_by(
            message_id='1578083234-893239-2956-1311577-2').first()
        self.assertFalse(m)


class RecipientModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config.TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_recipient(self):
        message_id = '1578083234-893239-2956-1311577-1'
        action = 'allowed'
        reason = ''
        reason_extra = ''
        delivered = 'delivered'
        delivery_detail = 'mail.protonmail.ch:25:250 2.0.0 OK: queued as \
                           01BF74010077'
        email = 'bird_alerts@charliejuliet.net'
        r = Recipient(message_id=message_id, action=action, reason=reason,
                      reason_extra=reason_extra, delivered=delivered,
                      delivery_detail=delivery_detail, email=email)
        db.session.add(r)
        db.session.commit()
        db.session.refresh(r)
        r = Recipient.query.filter_by(id=r.id).first()
        self.assertTrue(r)
        r = Recipient.query.filter_by(id=-1).first()
        self.assertFalse(r)


class AttachmentModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config.TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_recipient(self):
        message_id = '1578083234-893239-2956-1311577-1'
        name = 'Attachment1.docx'
        a = Attachment(message_id=message_id, name=name)
        db.session.add(a)
        db.session.commit()
        db.session.refresh(a)
        a = Attachment.query.filter_by(id=a.id).first()
        self.assertTrue(a)
        a = Attachment.query.filter_by(id=-1).first()
        self.assertFalse(a)


class AccountModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config.TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_set_account_name(self):
        a = Account(account_id='ESS000001')
        self.assertFalse(a.get_name())
        a.set_name('Test Name')
        self.assertTrue(a.get_name())


class DomainModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config.TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_set_domain_name(self):
        d = Domain(domain_id='201645')
        self.assertFalse(d.get_name())
        d.set_name('test.com')
        self.assertTrue(d.get_name())


if __name__ == '__main__':
    unittest.main(verbosity=2)
