from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.Integer, nullable=False)
    positivity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())

    def __repr__(self):
        return '<News %r>' % self.title
