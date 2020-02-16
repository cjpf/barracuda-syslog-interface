import unittest
import config
from app import create_app, db
from app.models import User, Message, Account, Domain


class TestConfig(config.BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
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
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_message(self):
        id = '1578083234-893239-2956-1311577-1'
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
        m = Message(id=id, account_id=account_id, domain_id=domain_id,
                    src_ip=src_ip, ptr_record=ptr_record, hdr_from=hdr_from,
                    env_from=env_from, hdr_to=hdr_to, dst_domain=dst_domain,
                    size=size, subject=subject, timestamp=timestamp)
        db.session.add(m)
        db.session.commit()
        m = Message.query.filter_by(
            id='1578083234-893239-2956-1311577-1').first()
        self.assertTrue(m)
        m = Message.query.filter_by(
            id='1578083234-893239-2956-1311577-2').first()
        self.assertFalse(m)

    # def test_add_recipient(self):

    # def test_add_attachment(self):

    # def test_add_account(self):

    # def test_add_domain(self):


class AccountModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_set_account_name(self):
        a = Account(id='ESS000001')
        self.assertFalse(a.get_name())
        a.set_name('Test Name')
        self.assertTrue(a.get_name())


class DomainModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_set_domain_name(self):
        d = Account(id='201645')
        self.assertFalse(d.get_name())
        d.set_name('test.com')
        self.assertTrue(d.get_name())


if __name__ == '__main__':
    unittest.main(verbosity=2)
