import jwt
import base64
import os
from datetime import datetime, timedelta
from time import time
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class PaginatedAPIMixin(object):
    '''
    A template for paginated resource collections
    '''
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint,
                                page=page,
                                per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint,
                                page=page + 1,
                                per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint,
                                page=page - 1,
                                per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class User(PaginatedAPIMixin, UserMixin, db.Model):
    '''
    User Model
    UserMixin provides default properties and methods for flask_login
    https://flask-login.readthedocs.io/en/latest/
    '''
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return '<User[{}] {}>'.format(self.id, self.email)

    def set_password(self, password):
        '''
        Set the users password
        '''
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        '''
        Check the users password
        '''
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        '''
        Generate one-time password reset token
        '''
        return jwt.encode(
            {
                'reset_password': self.id,
                'exp': time() + expires_in
            },
            current_app.config['SECRET_KEY'], algorithm='HS256'
        ).decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        '''
        Verify token in URL for password reset
        '''
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception as e:
            print(e)  # TODO log exception
            return
        return User.query.get(id)

    def to_dict(self):
        '''
        Converts a User object to a Python dict
        This will later be converted to JSON format
        '''
        data = {
            'id': self.id,
            'email': self.email,
            'last_seen': self.last_seen.isoformat() + 'Z',
            '_links': {
                'self': url_for('api.get_user', id=self.id)
            }
        }
        return data

    def from_dict(self, data, new_user=False):
        '''
        Converts a Python dict to a User object
        '''
        for field in ['email', 'last_seen']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        '''
        Returns the user token for AuthN / AuthZ
        '''
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        '''
        Revoke user token by setting expiration to 1 second ago
        '''
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        '''
        Returns user who owns token if it is a valid
        '''
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


class Message(PaginatedAPIMixin, db.Model):
    '''
    Message Model
    This model represents an email that passed through Barracuda Email
    Security Service
    '''
    message_id = db.Column(db.String(32), primary_key=True)
    account_id = db.Column(db.String(12), db.ForeignKey('account.account_id'))
    account = db.relationship(
        'Account', backref=db.backref('messages', lazy='dynamic'))
    domain_id = db.Column(db.String(12), db.ForeignKey('domain.domain_id'))
    domain = db.relationship(
        'Domain', backref=db.backref('messages', lazy='dynamic'))
    src_ip = db.Column(db.String(16), index=True)
    ptr_record = db.Column(db.String(128))
    hdr_from = db.Column(db.String(256))
    env_from = db.Column(db.String(256))
    hdr_to = db.Column(db.String(256))
    dst_domain = db.Column(db.String(128))
    size = db.Column(db.Integer)
    subject = db.Column(db.String(512))
    timestamp = db.Column(db.String(128))

    def __repr__(self):
        return '<Message {}>'.format(self.message_id)

    def to_dict(self):
        '''
        Converts a Message object to a Python dict
        This will later be converted to JSON format
        For retrieving
        '''
        data = {
            'message_id': self.message_id,
            'account_id': self.account_id,
            'src_ip': self.src_ip,
            'ptr_record': self.ptr_record,
            'hdr_from': self.hdr_from,
            'env_from': self.env_from,
            'hdr_to': self.hdr_to,
            'dst_domain': self.dst_domain,
            'size': self.size,
            'subject': self.subject,
            'timestamp': self.timestamp,
            '_links': {
                'self': url_for('api.get_message', message_id=self.message_id)
            }
        }
        return data

    def from_dict(self, data):
        '''
        Converts a Python dict to a Message object
        For creating Messages
        '''
        for field in [
            'message_id',
            'account_id',
            'src_ip',
            'ptr_record',
            'hdr_from',
            'env_from',
            'hdr_to',
            'dst_domain',
            'size',
            'subject',
            'timestamp'
        ]:
            if field in data:
                setattr(self, field, data[field])


class Recipient(db.Model):
    '''
    Recipient Model
    This model represents the recipient for an email
    '''
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(32), db.ForeignKey('message.message_id'))
    message = db.relationship(
        'Message', backref=db.backref('recipients', lazy='dynamic'))
    action = db.Column(db.String(32))
    reason = db.Column(db.String(64))
    reason_extra = db.Column(db.String(256))
    delivered = db.Column(db.String(32))
    delivery_detail = db.Column(db.String(1024))
    email = db.Column(db.String(128))

    def __repr__(self):
        return '<Recipient {}, from Message {}>'.format(self.id,
                                                        self.message_id)


class Attachment(db.Model):
    '''
    Attachment Model
    This model represents an attachment from an email
    '''
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(32), db.ForeignKey('message.message_id'))
    message = db.relationship(
        'Message', backref=db.backref('attachments', lazy='dynamic'))
    name = db.Column(db.String(256))

    def __repr__(self):
        return '<Attachment {}, from Message {}>'.format(self.id,
                                                         self.message_id)


class Account(PaginatedAPIMixin, db.Model):
    '''
    Account Model
    This model represents an ESS account
    '''
    account_id = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(128), unique=True)

    def __repr__(self):
        return '<Account {} {}>'.format(self.account_id, self.name)

    def set_name(self, name):
        '''
        Set the Account Name
        '''
        self.name = name

    def get_name(self):
        '''
        Get the Account Name
        '''
        return self.name

    def to_dict(self):
        '''
        Converts an Account object to a Python dict
        This will later be converted to JSON format
        For retrieving
        '''
        data = {
            'account_id': self.account_id,
            'name': self.name,
            '_links': {
                'self': url_for('api.get_account', account_id=self.account_id)
            }
        }
        return data

    def from_dict(self, data):
        '''
        Converts a Python dict to an Account object
        For creating
        '''
        for field in ['account_id', 'name']:
            if field in data:
                setattr(self, field, data[field])


class Domain(PaginatedAPIMixin, db.Model):
    '''
    Domain Model
    This model represents a domain from an ESS account
    '''
    domain_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(12), db.ForeignKey('account.account_id'))
    account = db.relationship(
        'Account', backref=db.backref('domains', lazy='dynamic'))
    name = db.Column(db.String(128), unique=True)

    def __repr__(self):
        return '<Domain {} {}>'.format(self.domain_id, self.name)

    def set_name(self, name):
        '''
        Set the Domain Name
        '''
        self.name = name

    def get_name(self):
        '''
        Get the Domain Name
        '''
        return self.name

    def to_dict(self):
        '''
        Converts a Domain object to a Python dict
        This will later be converted to JSON format
        For retrieving
        '''
        data = {
            'domain_id': self.domain_id,
            'account_id': self.account_id,
            'name': self.name,
            '_links': {
                'self': url_for('api.get_domain', domain_id=self.domain_id)
            }
        }
        return data

    def from_dict(self, data):
        '''
        Converts a Python dict to a Domain object
        For creating and setting values
        '''
        for field in ['domain_id', 'account_id', 'name']:
            if field in data:
                setattr(self, field, data[field])
