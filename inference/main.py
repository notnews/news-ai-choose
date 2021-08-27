"""
* use pre-trained model to infer sentiment score from event
"""
import re
import nltk
import pickle
import json
import boto3
import os
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

MODEL = None
VECTORIZER = None
ENGLISH_STOP_WORDS = None


def fetch_s3_data(bucket_name, key_name):
    """helper function to read objects direct from s3 storage"""
    s3 = boto3.resource("s3")
    return s3.Object(bucket_name, key_name).get()['Body'].read()


def get_english_stop_words():
    global ENGLISH_STOP_WORDS
    if ENGLISH_STOP_WORDS is None:
        ENGLISH_STOP_WORDS = pickle.loads(
            fetch_s3_data("news-you-choose",
                          'model-files/english_stop_words.pkl')
        )
    return ENGLISH_STOP_WORDS


def get_model_and_vectorizer():
    """Fetches the model and vectorizer pickle files. The vectorizer is too large for standard GitHub storage."""
    global MODEL
    global VECTORIZER
    if (MODEL is None) or (VECTORIZER is None):
        MODEL = pickle.loads(fetch_s3_data("news-you-choose",
                                           'model-files/lr_model.pkl'))  # model
        VECTORIZER = pickle.loads(fetch_s3_data("news-you-choose",
                                                'model-files/ngram_vectorizer.pkl'))  # vectorizer
    return MODEL, VECTORIZER


def preprocess_text(review):
    REPLACE_NO_SPACE = re.compile("[.;:!\'?,\"()\[\]]")
    REPLACE_WITH_SPACE = re.compile("(<br\s*/><br\s*/>)|(\-)|(\/)")
    clean_text = REPLACE_NO_SPACE.sub("", review.lower())
    clean_text = REPLACE_WITH_SPACE.sub(" ", clean_text)

    return clean_text


def remove_stop_words(review):
    ENGLISH_STOP_WORDS = get_english_stop_words()
    return ' '.join([word for word in review.split() if word not in ENGLISH_STOP_WORDS])


def predict_sentiment(text, model, vectorizer):
    text = preprocess_text(text)
    text = remove_stop_words(text)
    txt_vec = vectorizer.transform([text])
    return {
        "sentiment": int(model.predict(txt_vec)[0]),
        "probabilities": model.predict_proba(txt_vec).tolist()
    }


def get_mysql_connection():
    """helper function to get mysql connection with sqlalchemy"""
    engine = create_engine(
        "mysql+pymysql://{user}:{password}@{host}/{db}".format(
            user=os.getenv("MYSQL_USERNAME"),
            password=os.getenv("MYSQL_PASSWORD"),
            host=os.getenv("MYSQL_HOST"),
            db=os.getenv("MYSQL_DATABASE")
        )
    )
    return engine


def insert_inferenced_record(article, prediction):
    engine = get_mysql_connection()
    with engine.begin() as conn:
        conn.execute(
            "INSERT INTO news (title, content, src, url, sentiment, score, user_approve, user_disapprove, date, image_url, json_response) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (article["title"], article["content"], article["src"],
             article["url"], prediction["sentiment"], np.max(
                 prediction["probabilities"][0]) * 100, 0, 0, article["date"], article["image_url"], json.dumps(prediction))
        )
    return


def handle_s3_event(event, context):
    """Infer a score based on the text content and write to MySQL db"""
    print(event)
    s3_key = event["Records"][0]["s3"]["object"]["key"]
    s3_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    articles = json.loads(fetch_s3_data(s3_bucket, s3_key))["data"]
    MODEL, VECTORIZER = get_model_and_vectorizer()
    for article in articles:
        text = article["text"]
        prediction = predict_sentiment(text, MODEL, VECTORIZER)
        insert_inferenced_record(article, prediction)

    return {
        "statusCode": 200,
        "message": "Successfully processed {} records.".format(len(articles)),
        "key": s3_key,
        "bucket": s3_bucket
    }


def build_http_response(response_body, status_code=200):
    res = {}
    # CORS Headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }
    res["headers"] = headers
    res["statusCode"] = status_code
    res["body"] = json.dumps(response_body)
    res["isBase64Encoded"] = False
    return res


def handle_other_event(event, context):
    response = None
    if "text" in event:
        response = predict_sentiment(
            event["text"], *get_model_and_vectorizer())

    if response is not None:
        return build_http_response(response)
    else:
        return build_http_response({"error": "No text provided"}, 400)


def handler(event, context):
    """main function that handles http requests sent to the lambda func"""
    print(event)
    if "Records" in event:
        return handle_s3_event(event, context)
    elif "text" in event["body"]:
        return handle_other_event(event, context)
    else:
        return build_http_response({"error": "No event provided", "event": event}, 400)


if __name__ == "__main__":
    """quick way to test this out locally"""
    res = handler(
        {
            "Records": [
                {
                    "s3": {
                        "bucket": {
                            "name": "news-you-choose"
                        },
                        "object": {
                            "key": "2021/08/23/fox.json"
                        }
                    }
                }
            ]
        },
        None
    )
    print(res)
