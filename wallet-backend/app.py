import os
import logging

import firebase_admin
import json
import pymongo
from firebase_admin import auth
from firebase_admin import credentials
#from affiliateMarketing.app2 import get_scrapped_data
from flask_restful import Api

from flask import Flask, request, jsonify, render_template

from requests_oauthlib.oauth1_auth import Client

# Create A Config To Store Values
config = {
    'twitter_consumer_key': '',
    'twitter_consumer_secret': ''
}


app = Flask(__name__)

api = Api(app)

# Initialize Our OAuth Client
oauth = Client(config['twitter_consumer_key'], client_secret=config['twitter_consumer_secret'])


# create instance
logging.basicConfig(level=logging.INFO)


cred = credentials.Certificate("wallet-4120d-firebase-adminsdk-f6pth-78371b2e31.json")
firebase_admin.initialize_app(cred)


mClient = pymongo.MongoClient("mongodb+srv://ahmaddorra:XXXXX@cluster0.8sb8q.mongodb.net/?retryWrites=true&w=majority")
db = mClient.wallet
usersCollection = db.users
adsCollection = db.ads


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/get-ad", methods=["GET","POST"])
def getAds():
    """Provide tailored ads API route. Responds to both GET and POST requests."""
    logging.info("Get-ads request received!")
    email = request.args.get("email")
    user = auth.get_user_by_email(email)
    logging.info('Successfully fetched user data: {0}'.format(user.uid))
    ad = usersCollection.find_one( {}, {"email" : email, "adUrl": True})
    logging.info(ad)
    
    return json.dumps({"url": ad['adUrl']})
    
@app.route("/api/register-user", methods=["GET","POST"])
def registerUser():
    """Register users API route. Responds to both GET and POST requests."""
    logging.info("register-user request received!")
    email = request.args.get("email")
    user = auth.get_user_by_email(email)
    logging.info('Successfully fetched user data: {0}'.format(user.uid))
    logging.info(user)
    userData = {"uid": user.uid, "email": user.email}
#    usersCollection.insert_one(userData)
#    get_scrapped_data(email)
    
    logging.info('Successfully inserted user data: {0}'.format(user.uid))
    return jsonify({"data": user.uid})
    
@app.route("/api/connect-to-twitter", methods=["GET","POST"])
def connectToTwitter():
    """Register users API route. Responds to both GET and POST requests."""
    logging.info("connect-to-twitter request received!")
    email = request.args.get("email")
    
@app.route("/terms", methods=["GET"])
def terms():
    return jsonify({"message": "terms"})
    
@app.route("/privacy", methods=["GET"])
def privacy():
    return jsonify({"message": "privacy"})
    
from twitter import TwitterAuthenticate, TwitterCallback

api.add_resource(TwitterAuthenticate, '/authenticate/twitter')
api.add_resource(TwitterCallback, '/callback/twitter') # This MUST

if __name__ == '__main__':
  app.run(host='0.0.0.0',debug=True, port=os.environ.get("PORT", 5000))
