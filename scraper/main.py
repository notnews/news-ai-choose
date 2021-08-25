"""
Utility script for fetching top news articles from RSS feeds.
"""

import json
import boto3
import datetime
import feedparser
from newspaper import Article

SOURCES = {
    "cnn": "http://rss.cnn.com/rss/cnn_topstories.rss",
    "nytimes": "http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "fox": "http://feeds.foxnews.com/foxnews/latest"
}

DATA_DIR = "/tmp/json_data"


def upload_to_s3(data, source):
    """copy data from the /tmp/json_data directory to s3://news-you-choose/2021/08/16/ date partitioned key"""
    date_string = datetime.datetime.now().strftime("%Y/%m/%d")
    client = boto3.client('s3')
    client.put_object(
        Bucket='news-you-choose',
        Key=f"{date_string}/{source}.json",
        Body=json.dumps(data),
        ContentType='application/json'
    )
    return


def clean_text(article_text):
    if "<div" in article_text:
        article_text = article_text.split("<div")[0]
    return article_text


def get_articles_from_rss(source):
    """
    Get articles from a given RSS feed.
    """
    feed = feedparser.parse(source)
    return [article for article in feed.entries]


def parse_article_body(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text


def article_to_json(article_rss, article_body):
    dt = article_rss.published_parsed
    media = article_rss.get("media_content", "")
    return {
        "title": article_rss.title,
        "content": article_rss.summary,
        "src": "".join(article_rss.link.split("/")[:3]),
        "url": article_rss.link,
        "date": datetime.datetime(dt[0], dt[1], dt[2]).strftime("%Y-%m-%d"),
        "image_url": media[0]["url"] if media else "",
        "text": article_body,
    }


def handler(event, context):
    """main function to scrape and upload to s3"""
    for source, rss_link in SOURCES.items():
        data = {"data": []}
        articles = get_articles_from_rss(rss_link)
        for article_rss in articles:
            if not article_rss.get("published_parsed", ""):
                continue
            url = article_rss["links"][0]["href"]
            article_body = parse_article_body(url)
            article_rss.summary = clean_text(article_rss.summary)
            article_body_cleaned = clean_text(article_body)
            article_json = article_to_json(article_rss, article_body_cleaned)
            data["data"].append(article_json)
        upload_to_s3(data, source)
    return "Done!"
