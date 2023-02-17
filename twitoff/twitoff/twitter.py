# pylint: disable=import-error
from os import getenv
import tweepy
import spacy 
from .models import DB, Tweet, User

# get API Key from environment variables

key = getenv('TWITTER_API_KEY')
secret = getenv('TWITTER_API_KEY_SECRET')

# connect to the Twitter API

TWITTER_AUTH = tweepy.OAuthHandler(key, secret)
TWITTER = tweepy.API(TWITTER_AUTH)

def add_or_update_user(username):
    try:
        # gets back twitter user object
        twitter_user = TWITTER.get_user(screen_name=username)
        # Either updates or adds user to our DB
        db_user = (User.query.get(twitter_user.id)) or User(id=twitter_user.id, username=username)
        DB.session.add(db_user) # Add user if they don't exist

        #get the user's tweets

        tweets = twitter_user.timeline(count=200, exclude_replies=True, include_rts=False, tweet_mode='extended',since_id=db_user.newest_tweet_id)

        #check to see if the newest tweet in the DB is equal to the newest
        # tweet from the Twitter API, if they are not equal then that means
        # that the user has posterd new tweets that we should add to out DB
        if tweets:
            db_user.newest_tweet_id = tweets[0].id
            # tweets is a list of tweet objects
        for tweet in tweets:
            db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:300])
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    
    except Exception as e:
        print("Error processing{}: {}".format(username, e))
        raise e
    else:
        DB.session.commit()

# Load our pretrained SpaCy Word Embeddings model
nlp = spacy.load("my_model/")

#Turn tweet text into word embeddigns.
def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector
def update_all_users():
    usernames = []
    Users = User.query.all() 
    for user in Users:
        usernames.append(user.username)
    return usernames