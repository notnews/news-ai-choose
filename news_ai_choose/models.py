from datetime import datetime

from sqlalchemy.inspection import inspect
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


class News(db.Model, Serializer):
    __tablename__ = 'news'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.Integer, nullable=False)
    positivity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())

    def serialize(self):
        serial = Serializer.serialize(self)
        serial["created_at"] = serial["created_at"].strftime("%Y-%m-%d %H:%M%:%S")
        serial["updated_at"] = serial["updated_at"].strftime("%Y-%m-%d %H:%M%:%S")
        return serial
    
    def __repr__(self):
        return '<News %r>' % self.title
