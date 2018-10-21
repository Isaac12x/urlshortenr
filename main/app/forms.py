from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField
from wtforms.validators import DataRequired


class ShortenUrlForm(FlaskForm):
    # needs checking the passed data contains 'http or https or starts with www. app. or login. and nothign else'
    url = StringField('url', validators=[DataRequired()])
    recaptcha = RecaptchaField()
