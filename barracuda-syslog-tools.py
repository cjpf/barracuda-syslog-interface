from app import create_app, db
from app.models import User, Message, Recipient, Attachment, Account, Domain
import config


app = create_app(config.DevelopmentConfig)


@app.shell_context_processor
def make_shell_context():
    'Sets the context for flask shell'
    return{
        'db': db,
        'User': User,
        'Message': Message,
        'Recipient': Recipient,
        'Attachment': Attachment,
        'Account': Account,
        'Domain': Domain
    }
