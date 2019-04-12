import datetime
import inspect
import os
import uuid
import requests

from flask import Flask, send_from_directory, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from sqlalchemy import select
from werkzeug.exceptions import Forbidden, NotFound

SCRAPPING_APP_VERSION = '0.1.0'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL'] or 'sqlite:///' + os.path.join(f"{BASE_DIR}/migrations/", 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
# manager.add_command('db', MigrateCommand)
# manager.add_command("runserver", Server(host="0.0.0.0", port=5000))

SECRET_KEY = os.environ['SECRET_KEY']
PATH = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
BASE_URL = "https://bae-webapi.blockchainartexchange.io/api/artwork/get/"
TAG_URL = "https://bae-webapi.blockchainartexchange.io/api/tag/listforartwork/"


class ArtworkPointer(db.Model):
    artpiece_id = db.Column(db.String(36), index=True, unique=True, nullable=False, primary_key=True)
    block_id = db.Column(db.Integer, primary_key=False)
    name = db.Column(db.String(600), index=True, unique=True)
    url = db.Column(db.String(450), index=True, unique=True)
    page_url = db.Column(db.String(300), index=True, unique=True)
    created_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, index=True
    )

    def gen_page_urls(self):
        self.page_url =  f"https://blockchainartexchange.io/artwork/{self.artpiece_id}"
        db.session.add(self)
        db.session.commit()

    # def save(self):
    #     db.session.add(self)
    #     db.session.commit()

def get_token_metadata(id):
    resp = requests.get(f"{BASE_URL}{id}")
    parsed = resp.json()
    return parsed

def load_ids_in_memory(file_path, file_to_thumb):
    with open(file_path, 'r') as f, open(file_to_thumb, 'r') as t:
        for id, url in zip(f, t):
            # removes the \n of the file
            artpiece_id = ArtworkPointer(artpiece_id=id[:-1], url=url[:-1])
            db.session.add(artpiece_id)
            db.session.commit()


def _add_attribute(existing, attribute_name, options, token_id, display_type=None):
    trait = {
        'trait_type': attribute_name,
        'value': options[token_id % len(options)]
    }
    if display_type:
        trait['display_type'] = display_type
    existing.append(trait)

@app.route("/api/<token_id>", methods=["GET"])
def gen_token_data(token_id):
    resp = get_token_metadata(token_id)
    current_artpice = ArtworkPointer.query.get(id)
    current_artpiece.name = resp['artwork']['name']
    db.session.add(current_artpice)
    db.session.commit()

    return jsonify({
      "description": resp['artwork']['notes'],
      "external_url": current_artpice.page_url,
      "image": current_artpice.url,
      "name": resp['artwork']['name'],
      "attributes": [
        {'trait_type': 'Artwork type',
         'value': resp['artwork']["artworkGrade"]["artworkType"]
        },
        {'trait_type': 'Grade',
         'value': resp['artwork']["artworkGrade"]["overallGrade"]
        },
      ]
    })


if __name__ == '__main__':
    # manager.run()
    app.run(host="0.0.0.0", port="5000", debug=True, use_reloader=True)
