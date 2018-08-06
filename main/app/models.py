from main.app import db
from datetime import datetime


class Link(db.Model):
    """This class represents the links table."""

    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String, index=True, unique=True)
    target_url = db.Column(db.String, index=True, unique=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Link from==>{} to==>{} >'.format(
            self.original_url, self.target_url
        )
