# FeedlyRanking
A python script that scrapes your RSS (Feedly) feed and ranks articles using Word Mover's Distance and the Jaccard Index, according to keywords provided in keywords.txt

### SETUP
type keywords into keywords.txt, one keyword per line
### Install dependencies in python virtual environment
In the directory of the project
```
python3 -m venv ./venv (or any path you prefer)
source venv/bin/activate
pip3 install -r requirements.txt
```
### Run Code
'''
python3 feedly.py
(when it has finished)
python3 dashboard.py
'''
And navigate to the localhost url to view/interact with results
