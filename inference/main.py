"""
* use pre-trained model to infer sentiment score from event
"""
import pickle
import json
import boto3
import os
import numpy as np
from sqlalchemy import create_engine
import tempfile
from tensorflow import keras
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.models import Sequential


MODEL = None
TOKENIZER = None
ENGLISH_STOP_WORDS = None


def fetch_s3_data(bucket_name, key_name):
    """helper function to read objects direct from s3 storage"""
    s3 = boto3.resource("s3")
    return s3.Object(bucket_name, key_name).get()['Body'].read()


def get_model():
    """helper function to load the keras model weights
    Keras expects a file object, not a bytestring"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        model_path = os.path.join(tmpdirname, "model.h5")
        s3_model_data = fetch_s3_data(
            "news-you-choose", "model-files/tf-model/sentiment_model_v2.h5")
        with open(model_path, "wb") as f:
            f.write(s3_model_data)
        return keras.models.load_model(model_path)


def get_model_and_vectorizer():
    """Fetches the model and vectorizer pickle files. The vectorizer is too large for standard GitHub storage."""
    global MODEL
    global TOKENIZER
    if (MODEL is None) or (TOKENIZER is None):
        MODEL = get_model()  # model
        TOKENIZER = pickle.loads(fetch_s3_data("news-you-choose",
                                               'model-files/tf-model/tokenizer.pickle'))  # vectorizer
    return MODEL, TOKENIZER


def predict_sentiment(text: str, model: Sequential, tokenizer: Tokenizer):
    text = tokenizer.texts_to_sequences([text])
    text = pad_sequences(
        text, maxlen=512, padding='pre', truncating='pre')
    prediction = model.predict(text)
    pred_sentiment = np.argmax(prediction, axis=-1)[0]
    pred_text = ['NEGATIVE', 'NEUTRAL', 'POSITIVE'][pred_sentiment]
    return {
        "sentiment": int(pred_sentiment),
        "probabilities": prediction.tolist()[0],
        "sentiment_text": pred_text
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
    s3_key = event["Records"][0]["s3"]["object"]["key"]
    s3_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    articles = json.loads(fetch_s3_data(s3_bucket, s3_key))["data"]
    MODEL, TOKENIZER = get_model_and_vectorizer()
    for article in articles:
        text = article["text"]
        prediction = predict_sentiment(text, MODEL, TOKENIZER)
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
    # workaround for local testing
    try:
        event_body = json.loads(event["body"])
    except:
        event_body = event["body"]
    response = predict_sentiment(
        event_body["text"], *get_model_and_vectorizer())
    print(response)

    return build_http_response(response)


def handler(event, context):
    """main function that handles http requests sent to the lambda func"""
    print(event)
    if "Records" in event:
        return handle_s3_event(event, context)
    elif "body" in event:
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
