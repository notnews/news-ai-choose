import json
import os

from flask import Flask, render_template, jsonify, request
import requests

from . import models
from . import db_utils


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URI", "sqlite:///news_ai_choose.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/", methods=["GET", "POST"])
    def index():
        return render_template("index.html")

    @app.route("/articles", methods=["GET", "POST"])
    def articles():
        filtered_articles = models.News.query.filter_by(**request.json).all()
        to_json = [r.serialize() for r in filtered_articles]
        return jsonify(to_json)
    
    db = models.db
    db.app = app
    db.init_app(app)

    if os.getenv("FLASK_ENV") == "development":
        # simplifying a test db for local dev
        db.drop_all()
        db_utils.init_db()
        db_utils.populate_with_dev_data()

    return app