import json
import random

from . import models

def init_db():
    print("creating database and tables")
    models.db.create_all()
    print("database and tables created")


def populate_with_dev_data():
    with open("dummy_data.json", "r") as json_data:
        test_data = json.loads(json_data.read())
    
    test_articles = test_data["article_list"]["results"]
    for art in test_articles:
        new_art = models.News(
            title=art["title"],
            content=art["body"],
            category=random.randint(0, 4),
            positivity=random.randint(0, 2),
        )
        models.db.session.add(new_art)
        models.db.session.commit()
