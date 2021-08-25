# News A.I. Choose

The goal of New A.I. Choose is to train machine learning models to accurately predict the category of a news article based on the article body and other context clues. Additionally, this project intends to provide a front-end web interface for users to interact with stories by requesting more positive or more negative new stories. Users will also be able to assist the model by verifying if the recommendation is accurate - this will be used in future training to fine tune the models.

# ECR, Lambda and Deployments

We are using ECR along with a lambda function to run some web scraping tasks for this project. Read a quick [tutorial on this here](https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/).

## ECR repositories:

- `news-you-choose`
  - Contains the scraper for daily news articles
  - Used in Lambda function `news-you-choose-daily-scraper`
- `news-you-choose-inference`
  - Contains the model inference/api endpoint
  - Expects either
    - An S3 [event notification](https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-content-structure.html)
    - Or a JSON string with a "text" key: `{"text": "I like this article"}`

## Deployment to Lambda

Deployments to Lambda are currently manual, while we research how to do this manually.

1. alter the files in `scraper/` or `inference/` directories
   - Note that you can test this locally as described in the [tutorial](https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/).
2. run `make latest` to login, build and push the latest version of the image to the ECR repository as `news-you-choose:latest`
3. Go to the Lambda function on the aws console -> click `Image` -> `Deploy New Image` -> click `Browse Images` and choose the image with the `latest` tag

# Inference

Example requests and responses:

```shell
# build and run test container locally
$ cd inference/ && docker build . --tag inference:latest
...
$ docker run -p 9000:8080 -e AWS_ACCESS_KEY_ID=<your_key> -e AWS_SECRET_ACCESS_KEY=<you_secret> inference:latest
...

# simple sentiment score and probability
$ curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"text": "I love this movie"}'
{"sentiment": 4, "probabilities": [[0.14240485697747318, 0.8575951430225268]]}

# event-driven inference and record insertion
$ curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"Records": [{"s3": {"bucket": {"name": "news-you-choose"},"object": {"key": "2021/08/22/fox.json"}}}]}'
{"statusCode": 200, "message": "Successfully processed 10 records.", "key": "2021/08/22/fox.json", "bucket": "news-you-choose"}
```
