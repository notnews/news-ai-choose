from . import models

def init_db():
    print("creating database and tables")
    models.db.create_all()
    print("database and tables created")
