from app import create_app, db
from app.models import User
import config


app = create_app(config.DevelopmentConfig)


@app.shell_context_processor
def make_shell_context():
    'Sets the context for flask shell'
    return{'db': db, 'User': User}
