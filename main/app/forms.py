from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField
from wtforms.validators import DataRequired, URL

# did nto validate to be longer than our custom url because there is no point
# what if I still want to do it?
class ShortenUrlForm(FlaskForm):
    url = StringField('url', validators=[DataRequired(), URL(require_tld=False)])
    recaptcha = RecaptchaField()

class Extras(FlaskForm):
    pass
