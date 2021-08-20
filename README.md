# News A.I. Choose

The goal of New A.I. Choose is to train machine learning models to accurately predict the category of a news article based on the article body and other context clues. Additionally, this project intends to provide a front-end web interface for users to interact with stories by requesting more positive or more negative new stories. Users will also be able to assist the model by verifying if the recommendation is accurate - this will be used in future training to fine tune the models.

# ECR, Lambda and Deployments

We are using ECR along with a lambda function to run some web scraping tasks for this project. Read a quick [tutorial on this here](https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/).

## ECR repositories:

- `news-you-choose`
  - Contains the scraper for daily news articles
  - Used in Lambda function `news-you-choose-daily-scraper`

## Deployment to Lambda

Deployments to Lambda are currently manual, while we research how to do this manually.

1. alter the files in `scraper/` directory
   - Note that you can test this locally as described in the [tutorial](https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/).
2. run `make latest` to login, build and push the latest version of the image to the ECR repository as `news-you-choose:latest`
3. Go to the Lambda function on the aws console -> click `Image` -> `Deploy New Image` -> click `Browse Images` and choose the image with the `latest` tag
