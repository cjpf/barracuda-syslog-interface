from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from app.models import Domain


class SetDomainForm(FlaskForm):
    domain_name = StringField('Domain Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, domain_id, *args, **kwargs):
        super(SetDomainForm, self).__init__(*args, **kwargs)
        original_domain_name = Domain.query.filter_by(
            domain_id=domain_id).first().name
        self.original_domain_name = original_domain_name

    def validate_domain_name(self, domain_name):
        if domain_name.data != self.domain_name:
            name = Domain.query.filter_by(name=self.domain_name.data).first()
            if name is not None:
                raise ValidationError('Domain name taken. Please try again.')
