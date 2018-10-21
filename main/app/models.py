from main.app import db
from datetime import datetime


class Link(db.Model):
    """This class represents the links table."""

    __tablename__ = 'links'

    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String, index=True, unique=True)
    target_url = db.Column(db.String, index=True, unique=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Link from==>{self.original_url} to==>{self.target_url} >'


class Metadata(db.Model):
    """ This class represents the metadata of the link class"""

    # __tablename__ = 'link_meta'

    link_id = db.Column(db.Integer, db.ForeignKey('link.id'))
    views = db.relationship('View', backref='view', lazy='dynamic')
    allowed_more_than_one_view = db.Column(db.Boolean, default=True)
    self_destructing = db.Column(db.Boolean, default=False)
    has_tags = db.Column(db.Boolean, default=False)
    has_marketing_tags = db.Column(db.Boolean, default=False)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'Metadata of link with id f{self.link_id}'

    # calculate views
    @property
    def total_views(self):
        return len(self.views)



class View(db.Model):
    """ This class represents viewings of a link"""

    # __tablename__ = 'link_views'

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip = db.Column(db.String, index=True, unique=False)
    ip_location = db.Column(db.string, index=True, unique=False)

    def __repr__(self):
        # should get link id for this one via link_id of parent
        return f'View on link with id: '
