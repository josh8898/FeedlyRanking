# FeedlyRanking
A python script that scrapes your RSS (Feedly) feed and ranks articles using Word Mover's Distance and the Jaccard Index, according to keywords provided in keywords.txt. A feedly developer account and developer access token is required for this. Details on how to get that can be found [here.](https://developer.feedly.com/v3/developer/)
Dashboard displays the Title, URL, Section, Keywords (if provided), Summary, Word Mover's Distance, Jaccard Index of each article, ranked descending.

### SETUP
- add .env to directory, with KEY={your developer access token}
- type keywords into keywords.txt, one keyword per line
### Install dependencies in python virtual environment
In the directory of the project
```
python3 -m venv ./venv (or any path you prefer)
source venv/bin/activate
pip3 install -r requirements.txt
```
### Run Code
```
python3 feedly.py
(when it has finished)
python3 dashboard.py
```
And navigate to the localhost url to view/interact with results
