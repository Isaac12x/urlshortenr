import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    TESTING=True
    #CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT = int(os.environ.get("PORT", 5000))
    WTF_CSRF_ENABLED = True if os.environ.get("DEBUG") == False else False
    WTF_CSRF_SECRET_KEY = 'KVVLRCPGAOABCISAZGCMCBTHOZZBEELZYSGHSXXY99TSEMMFZSVIFWSGGOWAAXSJINRWSHQDEXLASWCCU'
    RECAPTCHA_PUBLIC_KEY='6LcMkHUUAAAAAAFUQSfgVcpBPADCXNmOg0YO5lwT'
    RECAPTCHA_PRIVATE_KEY='6LcMkHUUAAAAABgZ79x_38RQp_zsXrNz6qqWJZc0'
    RECAPTCHA_API_SERVER=''
    RECAPTCHA_PARAMETERS = {'render': 'explicit', 'data-size': "invisible"}
    RECAPTCHA_DATA_ATTRS = {'theme': 'light'}
