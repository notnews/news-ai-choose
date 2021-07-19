# News A.I. Choose
The goal of New A.I. Choose is to train machine learning models to accurately predict the category of a news article based on the article body and other context clues. Additionally, this project intends to provide a front-end web interface for users to interact with stories by requesting more positive or more negative new stories. Users will also be able to assist the model by verifying if the recommendation is accurate - this will be used in future training to fine tune the models.

# Development
set up and activate virtual environment, install requirements
```shell
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

start a local dev session by running `./local_dev.sh`. The database is currently populated by the test data stored in the file `dummy_data.json` which is a the result of a curl request to the nyt article api.

If this is your first time running the shell script you may need to `chmod +x local_dev.sh`


## Article API
Example of curl for getting articles based on some query parameter. All columns in models.News are able to be used in this JSON filter.
```shell
$ curl -X POST http://127.0.0.1:5000//articles --data '{"positivity": 1}' -H "Accept: application/json" -H "Content-Type: application/json"
```
Gets you the following structure:

```json
[
  {
    "category": 4, 
    "content": "CIMARRON, Kan. -- The ubiquitous swerving and darting forms making their hopscotch journey across the landscape here in recent days are part of one of the most storied -- and least celebrated -- natural migrations on the Great Plains. Yes, the tumbleweeds are on the move again. Over the coming weeks, more and more of these vagabond bundles of", 
    "created_at": "2021-07-18 21:28:50", 
    "id": 2, 
    "positivity": 1, 
    "title": "Drifting Along, Tumbleweeds Are Piling Up Across Plains", 
    "updated_at": "2021-07-18 21:28:50"
  }, // cutoff for brevity 
```
