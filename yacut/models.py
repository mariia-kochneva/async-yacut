from datetime import datetime

from yacut import db
from .constants import MAX_ORIGINAL_LENGTH, MAX_SHORT_LENGTH


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_ORIGINAL_LENGTH), nullable=False)
    short = db.Column(db.String(MAX_SHORT_LENGTH), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<URLMap {self.short} -> {self.original[:50]}>'

    def to_dict(self):
        return {'url': self.original}
