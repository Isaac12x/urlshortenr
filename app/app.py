import datetime
import inspect
import os
import uuid
import requests

from flask import Flask, send_from_directory, flash, request, redirect, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from sqlalchemy import select
from werkzeug.exceptions import Forbidden, NotFound
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, SelectField, DateField
from wtforms.fields.html5 import URLField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, StopValidation
from config import Config
from uuid import uuid4

SCRAPPING_APP_VERSION = "0.1.0"

import logging
from logging.handlers import SMTPHandler

mail_handler = SMTPHandler(
    mailhost='127.0.0.1',
    fromaddr='server-error@blockchainartexchange.com',
    toaddrs=['isaac@mammbo.com'],
    subject='Application Error'
)
mail_handler.setLevel(logging.ERROR)
mail_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
# manager.add_command('db', MigrateCommand)
# manager.add_command("runserver", Server(host="0.0.0.0", port=5000))
if not app.debug:
    app.logger.addHandler(mail_handler)


PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
BASE_URL = "https://bae-webapi.blockchainartexchange.io/api/artwork/get/"
TAG_URL = "https://bae-webapi.blockchainartexchange.io/api/tag/listforartwork/"
FILE_URL = "https://bae-fs.blockchainartexchange.io/"

class Artpiece(db.Model):
    artpiece_id =  db.Column(db.String(36), index=True, unique=True, nullable=False, primary_key=True)
    artpiece_name = db.Column(db.String(100), index=True, unique=False)
    artwork_type = db.Column(db.String(100), index=True, unique=False)
    artpiece_explanation = db.Column(db.Text, index=False, unique=False, nullable=True)
    artist = db.Column(db.String(100), index=True, unique=False)
    artist_bio = db.Column(db.Text, index=False, unique=False, nullable=True)
    image_url = db.Column(db.String(450), index=True, unique=True)
    thumbnail_url = db.Column(db.String(450), index=True, unique=True, nullable=True)
    youtube_url = db.Column(db.String(450), index=True, unique=False, nullable=True)
    price = db.Column(db.Integer, primary_key=False)
    last_sold_for = db.Column(db.Integer, primary_key=False)
    website = db.Column(db.String(300), index=True, unique=False, nullable=True)
    is_for_sale = db.Column(db.Boolean)
    grade = db.Column(db.String(2), index=True, unique=False, nullable=True)
    remaining_printings = db.Column(db.Integer, primary_key=False, nullable=True)
    includes_physical = db.Column(db.Boolean, nullable=True)
    date_created = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
    notes = db.Column(db.Text, index=False, unique=False, nullable=True)

    def gen_token_uri(self):
        return f"Artwork name: {self.artpiece_name} -  token url: https://app.blockchainartexchange.io/api/get-metadata/{self.artpiece_id}"


class ArtworkPointer(db.Model):
    artpiece_id = db.Column(
        db.String(36), index=True, unique=True, nullable=False, primary_key=True
    )
    artist = db.Column(db.String(100), index=True, unique=False, nullable=True)
    block_id = db.Column(db.Integer, primary_key=False)
    name = db.Column(db.String(600), index=True, unique=False)
    notes = db.Column(db.Text, index=False, unique=False)
    image_url = db.Column(db.String(450), index=True, unique=True)
    page_url = db.Column(db.String(300), index=True, unique=True)
    meta_url = db.Column(db.String(300), index=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)

    def gen_page_url(self):
        self.page_url = f"https://blockchainartexchange.io/artwork/{self.artpiece_id}"
        db.session.add(self)
        db.session.commit()

    def gen_opensea_url(self):
        return f"Artwork name: {self.name} -  token url: https://app.blockchainartexchange.io/api/get-metadata/{self.artpiece_id}"

    def make_image_url(self):
        self.image_url = f"{FILE_URL}{self.image_url[0:2]}/{self.image_url[2:4]}/{self.image_url}-preview.jpg"
        db.session.add(self)
        db.session.commit()


def get_token_metadata(id):
    resp = requests.get(f"{BASE_URL}{id}")
    parsed = resp.json()
    return parsed


def load_ids_in_memory(file_path, file_to_thumb):
    with open(file_path, "r") as f, open(file_to_thumb, "r") as t:
        for id, url in zip(f, t):
            # removes the \n of the file
            artpiece_id = ArtworkPointer(artpiece_id=id[:-1], url=url[:-1])
            db.session.add(artpiece_id)
            db.session.commit()


def _add_attribute(existing, attribute_name, options, token_id, display_type=None):
    url = "https://bae-webapi.blockchainartexchange.io/api/tag/listforartwork/dfaa24da-a7c4-4a4b-9487-de44389d2b48"
    trait = {"trait_type": "Tag", "value": options[token_id % len(options)]}
    if display_type:
        trait["display_type"] = display_type
    existing.append(trait)


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


@app.route("/api/load-artpieces", methods=["GET"])
def load_all():
    resp = requests.get("https://bae-webapi.blockchainartexchange.io/api/artwork/list")
    parsed_resp = resp.json()

    artworks = [
        ArtworkPointer.query.get(p["id"])
        if ArtworkPointer.query.get(p["id"])
        else ArtworkPointer(
            artpiece_id=p["id"],
            artist=p["artist"]["name"],
            name=p["name"],
            notes=p.get("notes", ""),
            image_url=p["asset"]["id"],
        )
        for p in parsed_resp["artworks"]
    ]

    for artwork in artworks:
        if artwork.image_url:
            artwork.make_image_url()
            artwork.gen_page_url()

    [db.session.add(artwork) for artwork in artworks]
    db.session.commit()
    # should be loading
    try:
        return jsonify({"response": "success"})
    except Exception as e:
        return jsonify({"response": e})


@app.route("/api/get-metadata/<token_id>", methods=["GET"])
def gen_token_data(token_id):
    db_artpiece = Artpiece.query.get_or_404(token_id)
    if db_artpiece:
        return jsonify(
            {
                "description": db_artpiece.artpiece_explanation,
                "artist": db_artpiece.artist,
                "external_url": db_artpiece.website,
                "image": db_artpiece.image_url,
                "name": db_artpiece.artpiece_name,
                "attributes": [{
                    "trait_type": "Artwork type",
                    "value": db_artpiece.artwork_type,
                },
                {
                    "trait_type": "Grade",
                    "value": db_artpiece.grade,
                },
                {
                    "display_type": "number",
                    "trait_type": "Last sold for",
                    "value": db_artpiece.last_sold_for,
                },
                {
                    "display_type": "ranking",
                    "trait_type": "Prints remaining",
                    "value": db_artpiece.remaining_printings,
                },
                {
                    "trait_type": "Physical representation",
                    "value": db_artpiece.includes_physical,
                },
            ],
        })
    else:
        resp = get_token_metadata(token_id)
        current_artpiece = ArtworkPointer.query.get_or_404(token_id)
        if current_artpiece:
            last_sold_for = safe_cast(resp["artwork"]["price"], int, str)
            prints_remaining = safe_cast(resp["artwork"]["printsRemaining"], int, str)
            return jsonify(
                {
                    "description": current_artpiece.notes,
                    "artist": current_artpiece.artist,
                    "external_url": current_artpiece.page_url,
                    "image": current_artpiece.image_url,
                    "name": current_artpiece.name,
                    "attributes": [
                        {
                            "trait_type": "Artwork type",
                            "value": resp["artwork"]["artworkGrade"]["artworkType"],
                        },
                        {
                            "trait_type": "Grade",
                            "value": resp["artwork"]["artworkGrade"]["overallGrade"],
                        },
                        {
                            "display_type": "number",
                            "trait_type": "Last sold for",
                            "value": last_sold_for,
                        },
                        {
                            "display_type": "ranking",
                            "trait_type": "Prints remaining",
                            "value": prints_remaining,
                        },
                    ],
                }
            )

@app.route("/api/urls", methods=["GET"])
def generate_bulk_urls_opensea():
    artworks = ArtworkPointer.query.all()
    with open("open-sea-urls.txt", "w") as f:
        for art in artworks:
            f.write(art.gen_opensea_url())
    art = [art.gen_opensea_url() for art in artworks]
    return jsonify(art)


@app.route("/api/artworks", methods=["GET"])
def generate_bulk_urls():
    artworks = Artwork.query.all()
    with open("tokenURI.txt", "w") as f:
        for art in artworks:
            f.write(art.gen_opensea_url())
    art = [art.gen_token_uri() for art in artworks]
    return jsonify(art)



@app.route('/')
def handler():
    return redirect('/create-art-token', 302)

class ArtworkForm(FlaskForm):
    artist_name = StringField('Your name or pseudonym', validators=[DataRequired()], render_kw={"placeholder": "E.g. James brown"})
    artist_description = TextAreaField('Give a description of your work', render_kw={"placeholder": "Quick bio on yourself, motives or whatever you want to explain. This is not required."})
    artwork_type = SelectField('Artwork type', choices=[("V", "Video"), ("P", "Physical"), ("D", "Digital")])
    name_work = StringField('Name the artwork', validators=[Length(min=0, max=250)], render_kw={"placeholder": "E.g. Ethereal ether 1"})
    description = TextAreaField('Give a discription of the item', validators=[Length(min=0, max=300)], render_kw={"placeholder": "Explanation of the artwork..."})
    website = URLField('Link to your website or portfolio', validators=[], render_kw={"placeholder": "Your website or gallery url. This is not required."})
    image_url = URLField('Input an image url. It must end with the file type eg. .jpeg', validators=[], render_kw={"placeholder": "This IS required."})
    thumbnail_url = URLField('Input a thumbnail image url. It must end with the file type eg. .jpeg', validators=[], render_kw={"placeholder": "This is not required."})
    youtube_url = URLField('Input a youtube url if the artwork type is video.', validators=[], render_kw={"placeholder": "This is not required."})
    printings = IntegerField('Number of allowed printings of the artwork', validators=[], render_kw={"placeholder": "Default is 0"}, default=0)
    price = IntegerField('Price of the artwork', validators=[DataRequired()], render_kw={"placeholder": "This is required."})
    grade = StringField('Grade for the artwork', validators=[Length(min=0, max=3)],render_kw={"placeholder": "A+, A, ..."})
    last_sold_for = IntegerField('If sold before, what was the price then?', validators=[], render_kw={"placeholder": "This is not required."}, default=0)
    physical_copy = BooleanField("Includes physical copy?", validators=[], render_kw={"placeholder": "Default is false."})
    date_created = DateField(validators=[DataRequired()], render_kw={"placeholder": "When it was created"})
    notes =  TextAreaField('Additional Notes', validators=[Length(min=0, max=300)], render_kw={"placeholder": "Additional notes. This is not required."})
    submit =  SubmitField('Generate tokenURI')


@app.route('/create-art-token', methods=["GET", "POST"])
def generate_token_string_builder():
    form = ArtworkForm()
    try:
        if form.validate_on_submit():
            artwor_type = ""
            if form.artwork_type.data == "V":
                artwork_type = "Video"
            elif form.artwork_type.data == "P":
                artwork_type = "Physical"
            else:
                artwork_type = "Digital"
            artist = form.artist_name.data
            artist_description = form.artist_description.data
            artwork_type = artwork_type
            name_work = form.name_work.data
            description = form.description.data
            website = form.website.data
            image_url = form.image_url.data
            thumbnail_url = form.thumbnail_url.data
            youtube_url = form.youtube_url.data
            last_sold_for = form.last_sold_for.data
            grade = form.grade.data
            printings = form.price.data
            last_sold_for = form.last_sold_for.data
            price = form.price.data
            date_created = form.date_created.data
            physical_copy = form.physical_copy.data
            notes = form.notes.data


            gen = Artpiece(
                artpiece_id=str(uuid4()),
                artpiece_name=name_work,
                artpiece_explanation=description,
                artwork_type=artwork_type,
                artist=artist,
                artist_bio=artist_description,
                website=website,
                image_url=image_url,
                thumbnail_url=thumbnail_url,
                youtube_url=youtube_url,
                price=price,
                last_sold_for=last_sold_for,
                is_for_sale=True,
                grade=grade,
                remaining_printings=printings or 0,
                includes_physical=physical_copy,
                date_created=date_created,
                notes=notes or ''
            )

            db.session.add(gen)
            db.session.commit()

            flash(f'{gen.gen_token_uri()}')
    except Exception:
        flash(f"There is an error in the form - we are working on it right now")

    return render_template('token-form.html', title="", form=form)


if __name__ == "__main__":
    # manager.run()
    app.run(host="0.0.0.0", port="8000", debug=False, use_reloader=True)
