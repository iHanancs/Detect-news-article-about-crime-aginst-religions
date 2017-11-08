
#extract url of articles from http://religionnews.com/tag/hate-crime/
from bs4 import BeautifulSoup
import requests
import nltk
import newspaper
from newspaper import Article
import random 
import math

keywords= []
article_content = []

########## prepare training and testing data ##########
#prepare article content (positive example)
print("start prepare training and testing data ...")
url = "http://religionnews.com/tag/hate-crime/"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
result = requests.get(url, headers=headers)

soup = BeautifulSoup(result.content.decode(), 'html.parser')
result_art = soup.find(id="content")
poslist = []
for a in result_art.find_all('a', href=True):
   if a['href'] not in poslist and "/20" in a['href']:
     poslist.append(a['href'])

for article in poslist:
   a = Article(article)
   a.download()
   a.parse()
   article_content.append([(nltk.word_tokenize(a.text)),"pos"])
   a.nlp()
   keywords+=a.keywords

#prepare article content (negative example)

url = "http://religionnews.com/series/was-blind/"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
result = requests.get(url, headers=headers)

soup = BeautifulSoup(result.content.decode(), 'html.parser')
result_art = soup.find(id="content")
neglist = []
for a in result_art.find_all('a', href=True):
   if a['href'] not in neglist and "/20" in a['href']:
     neglist.append(a['href'])
     
for article in neglist:
     a = Article(article)
     a.download()
     a.parse()
     article_content.append([(nltk.word_tokenize(a.text)),"neg"])

      

#-----------------------------------
random.shuffle(keywords)
random.shuffle(article_content)


########## prepare feature ##########
print("start prepare features of model ...")

word_features = nltk.FreqDist(w.lower() for w in keywords)

#define a feature extractor
def extract_features(new):
    new_words = set(new)
    features = {}
    for word in word_features:
        features['contains({})'.format(word)] = (word in new_words)
    return features
    
featuresets = [(extract_features(d), c) for (d,c) in article_content]


#divide data to train set and test set
test_set, train_set = featuresets[math.floor(len(featuresets)/2)-1:], featuresets[:math.ceil(len(featuresets)/2)]


########## train classifier ##########
print("start prepare training classifier model ...")

#train classifier
classifier = nltk.NaiveBayesClassifier.train(train_set)

#evaluate the classifier on a much larger quantity of unseen data
print("the accuracy of model is: ", nltk.classify.accuracy(classifier, test_set))



#function to classify new example
def classify_news(url_article):
     a = Article(url_article)
     a.download()
     a.parse()
     a.nlp()
     tokens_article = nltk.word_tokenize(a.text)
     print("title:", a.title)
     return classifier.classify(extract_features(tokens_article))
print("Your article is . . .")
#to classify any article, put URL  of article here     
if classify_news("http://forward.com/news/325988/jews-are-still-the-biggest-target-of-hate-crimes/") == "neg":
   print("It's not about crime aginst religions")
else: print("It's about crime aginst religions")
     
   

