# News A.I. Choose

The goal of New A.I. Choose is to train machine learning models to accurately predict the category of a news article based on the article body and other context clues. Additionally, this project intends to provide a front-end web interface for users to interact with stories by requesting more positive or more negative new stories. Users will also be able to assist the model by verifying if the recommendation is accurate - this will be used in future training to fine tune the models.

# Pushing images to ECR

We are using ECS Fargate to run some web scraping tasks for this web application.

```shell
docker login -u AWS -p $(aws ecr get-login-password --region us-east-2 --profile fourthbrain) <aws_account_id>.dkr.ecr.us-east-2.amazonaws.com

docker build . --tag news_you_choose:latest

docker tag news-you-choose-scraper <aws_account_id>.dkr.ecr.us-east-2.amazonaws.com/news-you-choose:latest

docker push <aws_account_id>.dkr.ecr.us-east-2.amazonaws.com/news-you-choose:latest
```
