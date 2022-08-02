# Import our functions and Resource class from flask_restful
from flask_restful import Resource, reqparse

# Import our functions from Flask
from flask import redirect, request
import logging
import ast
import json
import pandas as pd
# Import our oauth object from our app
#from app.app import oauth
from requests_oauthlib.oauth1_auth import Client

import pymongo
# Import requests in order to make server sided requests
import requests
import threading
# import the module
import tweepy

from klangooclient.MagnetAPIClient import MagnetAPIClient

ENDPOINT ='https://nlp.klangoo.com/Service.svc'
CALK ='99a308bb-2046-497d-884a-7b20412fb6f4'
SECRET_KEY ='XXXXXX'
    

# Create A Config To Store Values
config = {
    'twitter_consumer_key': '',
    'twitter_consumer_secret': ''
}
MY_BEARER_TOKEN = "XXXXXX"


oauth = Client(config['twitter_consumer_key'], client_secret=config['twitter_consumer_secret'])

mClient = pymongo.MongoClient("mongodb+srv://ahmaddorra:XXXXX@cluster0.8sb8q.mongodb.net/?retryWrites=true&w=majority")
db = mClient.wallet
usersCollection = db.users
adsCollection = db.ads

class TwitterAuthenticate(Resource):
    def get(self):
        uri, headers, body = oauth.sign('https://twitter.com/oauth/request_token')
        res = requests.get(uri, headers=headers, data=body)
        res_split = res.text.split('&') # Splitting between the two params sent back
        oauth_token = res_split[0].split('=')[1] # Pulling our APPS OAuth token from the response.
        return redirect('https://api.twitter.com/oauth/authenticate?oauth_token=' + oauth_token, 302)

def callback_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('oauth_token')
    parser.add_argument('oauth_verifier')
    return parser

class TwitterCallback(Resource):
    def get(self):
        logging.info("here")
        parser = callback_parser()
        logging.info("here")
#        args = parser.parse_args() # Parse our args into a dict
        args = {'oauth_token': request.args.get("oauth_token"), 'oauth_verifier': request.args.get("oauth_verifier")}
        logging.info("here")
        res = requests.post('https://api.twitter.com/oauth/access_token?oauth_token=' + args['oauth_token'] + '&oauth_verifier=' + args['oauth_verifier']+ '&include_email=true')
        logging.info("here")
        logging.info(res.text)
        res_split = res.text.split('&')
        oauth_token = res_split[0].split('=')[1]
        oauth_secret = res_split[1].split('=')[1]
        username = res_split[3].split('=')[1]
        userid = res_split[2].split('=')[1]
        # authorization of consumer key and consumer secret
        auth = tweepy.OAuthHandler(config['twitter_consumer_key'], config['twitter_consumer_secret'])
          
        # set access to user's access key and access secret
        auth.set_access_token(oauth_token, oauth_secret)
          
        # calling the api
        api = tweepy.API(auth)
        user = api.verify_credentials(include_email=True)
        if  user == False:
            logging.info("The user credentials are invalid.")
        else:
            logging.info(user.email)
            logging.info("The user credentials are valid.")
        userData = {"oauth_token": oauth_token, "oauth_secret": oauth_secret, "userid": userid, "username": username, "email": user.email}
        thread = threading.Thread(target=putAd, name="putAd", args=(oauth_token,oauth_secret,userid, username, user.email))
        thread.start()
        return redirect('https://wallet-backend-dora.herokuapp.com/')
#http://localhost:5000/callback/twitter?oauth_token=05kv3gAAAAABaJxGAAABglerObY&oauth_verifier=uysC3rl1m3GiEk0wjH2kTCdFXfEOjnFW

def putAd(oauth_token,oauth_secret,userid, username, email):
    userData = {"oauth_token": oauth_token, "oauth_secret": oauth_secret, "userid": userid, "username": username, "email": email}
    logging.info(userData)
    ads = pd.read_csv('ads.csv',names=['index', 'topics','category'])
    
    tclient = tweepy.Client(bearer_token=MY_BEARER_TOKEN)
    # query to search for tweets
    query = "(from:"+userData["username"]+") -is:retweet"
    
    tweets = tclient.search_recent_tweets(query=query,
         tweet_fields = ["created_at", "text", "source","author_id","lang","context_annotations","entities"],
         user_fields = ["name", "username", "location", "verified", "description"],
         max_results = 20,
         expansions='author_id'
     )
    text = ""
    for tweet in tweets.data:
        text += " "+ tweet.text
    
    logging.info(text)
    kclient = MagnetAPIClient(ENDPOINT, CALK, SECRET_KEY)
    request = { 'text' : text, 'format' : 'json' }
    rsp = json.loads(kclient.callwebmethod('ProcessDocument', request, 'POST').decode('utf-8'))
    logging.info(rsp)
    result = []
    for category in rsp['document']['categories']:
        result.append(category['name'])
    recommended_ads = recommend_ads(result, ads)
    userData["adUrl"] = recommended_ads[0][0]
    userData["score"] = recommended_ads[0][1]
    logging.info(userData)
    usersCollection.insert_one(userData)
    logging.info("Successfully inserted ad")
    
    
def recommend_ads(user, ads):
    recommended_ads = []
    userdata = set(user)
    for i in range(ads.shape[0]):
        ad = set(ast.literal_eval(str(ads['topics'][i])) + ast.literal_eval(str(ads['category'][i])))
        common = float(len(userdata & ad)) / len(userdata) * 100
        if common > 20:
            recommended_ads.append([ads['index'][i], common])
    result = sorted(recommended_ads, reverse = True, key = lambda x: int(x[1]))
    return result

