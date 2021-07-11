"""Helper file for running this Flask app serverless"""
from news_ai_choose import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
