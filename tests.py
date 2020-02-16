import unittest
import config
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Account


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

    def test_password_hashing(self):
        u = User(email='susan@test.com')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))


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

    def test_account(self):
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

    def test_domain(self):
        d = Account(id='201645')
        self.assertFalse(d.get_name())
        d.set_name('test.com')
        self.assertTrue(d.get_name())


if __name__ == '__main__':
    unittest.main(verbosity=2)
