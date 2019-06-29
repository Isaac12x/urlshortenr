import os

class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        "{0}/migrations/".format(BASE_DIR), "app.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
