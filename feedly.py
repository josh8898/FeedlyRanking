print('Loading general libraries...\n')
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from dotenv import load_dotenv
import html
import json
import os
import requests
import time
import urllib.parse

# Function to return current timestamp
def get_ms_now():
	ms = int(time.time()) * 1000
	return ms

# Millisecond timestamp to date function
def ms_to_dt(timestamp):
	ms = timestamp / 1000
	dt = datetime.fromtimestamp(ms).strftime('%Y-%m-%dT%H:%M:%SZ')
	return dt

# Check json for a key:value pair and return value
def check_json_key(json_key, json_object):
	if json_key in json_object:
		return json_object[json_key]
	else:
		return '-'

# Get current timestamp less nominal 24 hours
newer_than = get_ms_now() - (86400 * 1000)

# Instantiate BART
print('Loading our BART model for the summaries...\n')
from transformers import BartForConditionalGeneration, BartTokenizer, BartConfig
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

#open output.csv, truncate, then write columns
f = open('output.csv', "w+")
f.truncate()
f.write("Datetime,Title,URL,Author,Section,Publication,Keywords,Summary,WMD_Distance,Jaccard Index\n")
f.close()

# Load API key
load_dotenv()
key = os.environ.get("KEY")


# Custom request header
headers = {
	'Authorization': key
}


# Base url
base_url = 'https://cloud.feedly.com/v3/'

#filter keyterms
my_file = open("keywords.txt", "r")
content = my_file.read()
terms = content.split('\n')
my_file.close()
# Send request to collections api and access data
url = base_url + 'collections'
response = requests.get(url, headers = headers)


# If request was successful, continue with the script
if response.ok:
	# Capture data
	results = json.loads(response.text)
else:
	print('Something went wrong, check the collections request.')
	exit()

arr = []


# Create a list of 'followed' feeds
collections = []
for result in range(len(results)):
	for feed in results[result]['feeds']:
		collections.append(feed['id'])
		print('{} has been added to your collection...\n'.format(feed['id']))


# Iterate through collections list
for collection in collections:

	# Encode feed id
	feed_id_raw = collection
	feed_id_enc = urllib.parse.quote(feed_id_raw, safe='')


	# Send request to streams api and access data
	url = base_url + 'streams/' + feed_id_enc + '/contents?count=1000&newerThan=' + str(newer_than)
	response = requests.get(url, headers = headers)


	# If request was successful, continue with the script
	if response.ok:
		# Capture data
		results = json.loads(response.text)
	else:
		print('Something went wrong, check the streams request.')
		exit()


	# Iterate through streams data
	for result in range(len(results['items'])):
		
		# Get article count
		article_count = result + 1

		# Check if date exists
		date = ms_to_dt(check_json_key('published', results['items'][result]))

		# Check if title exists
		title = check_json_key('title', results['items'][result])

		# Check if url exists
		url = check_json_key('alternate', results['items'][result])[0]['href']

		# Check if author exists
		author = check_json_key('author', results['items'][result])
		
		# Check if section exists
		section = check_json_key('title', results)

		# Check if publication exists
		publication = check_json_key('id', results)

		# Check if keywords exists
		keywords = check_json_key('keywords', results['items'][result])

		# Check if summary exists then check if content exists
		summary_raw = check_json_key('summary', results['items'][result])
		content = check_json_key('content', summary_raw)
		summary = BeautifulSoup(html.unescape(content), features="html.parser").text

		# Bart abstract text summarization
		if len(summary) > 2500:
			inputs = tokenizer.batch_encode_plus([summary], return_tensors='pt', max_length=100, truncation=True)
			summary_ids = model.generate(inputs['input_ids'], early_stopping=True)
			summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
 

		row = [date, title, url, author, section, publication, keywords, summary, 0, 0]
		arr.append(row)

#Gensim Word Mover's Distance
sentence_keywords = ' '.join(terms)
from nltk.corpus import stopwords
from nltk import download
import gensim.downloader as api
model = api.load('word2vec-google-news-300')
download('stopwords')  # Download stopwords list.
stop_words = stopwords.words('english')

#remove stopwords from our sentences
def preprocess(sentence):
    return [w for w in sentence.lower().split() if w not in stop_words]

sentence_keywords = preprocess(sentence_keywords)

#compute WMD using the ``wmdistance`` method.
#In simple terms, we are turning each word into an object.
#Each of these objects can be compared, and how similar
#each of the objects are represents how similar those words
#are semantically.
for row in arr:
	row_sentence = preprocess(row[1].lower() + " " + " ".join(row[6]).lower() + " " + row[7].lower())
	distance = model.wmdistance(sentence_keywords, row_sentence)
	distance = float("{0:.4f}".format(distance))
	row[8] = distance
	#Jaccard Index
	#In simple terms, this calculates the the intersection of
	#the two corpora, with the union, the find the percentage of
	#words in the text that match.
	set1 = set(row_sentence)
	set2 = set(terms)
	row[9] = len(set1.intersection(set2)) / len(set1.union(set2))

#sort array by amount of unique terms present in title/keywords/summary field
arr = sorted(arr, key=lambda x:x[8])
#dump array to .csv
for row in arr:
	with open('output.csv', 'a', encoding='utf-8-sig') as f:
		writer = csv.writer(f)
		writer.writerow(row)
