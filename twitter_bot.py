import tweepy
import time
import logging

from keys import *

"""
These are the keywords we will check to see if the mentions contain. 
"""
KEYWORDS = ['hello', 'greetings', 'salutations', 'hi']


def create_api():
    """
    Create API with auth info provided in keys.txt
    Return and log relevant errors.
    """
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(
        auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True
    )
    try:
        api.verify_credentials()
    except Exception as e:
        logging.error("Error creating API. Check Auth", exc_info=True)
        raise e
    logging.info("API created successfully")
    return api


def check_mentions(api, terms, last_seen_id):
    """
    Check if there  have been any @ mentions of the bot account.
    If so, check those mentions for keywords
    Check if the mention tweet is favourited, if not, favourite it
    Check if the user is followed, if not, follow them
    Reply to mention tweet
    If tweepy error for duplicate tweet, handle. 
    """
    logging.info("Retrieving mentions...")
    print("Retrieving mentions...")
    new_since = last_seen_id
    for tweet in tweepy.Cursor(api.mentions_timeline,
                               since_id=last_seen_id).items():
        new_since = max(int(tweet.id), new_since)
        if tweet.in_reply_to_status_id is not None:
            continue
        if any(keyword in tweet.text.lower() for keyword in terms):
            logging.info(f'Replying to {tweet.user.name}')
            print(f'Replying to {tweet.user.name}')

            if not tweet.favorited:
                tweet.favorite()
                logging.info(f'Favourited')
                print(f'Favourited...')
            if not tweet.user.following:
                tweet.user.follow()
                logging.info(f'Followed')
                print('Followed...')

            try:
                reply_status = "@" + tweet.user.name + ' Greetings human!' +\
                               '  -  ' + str(tweet.id)
                api.update_status(
                    status=reply_status,
                    in_reply_to_status_id=tweet.id
                )
            except tweepy.TweepError as e:
                logging.info(f'Tweet already replied to')
                print(f'Tweet already replied to')
                pass
            return new_since


def main(terms):
    """
    Setup API and run main loop
    """
    api = create_api()
    new_since = 1
    while True:
        new_since = check_mentions(api, list(terms), new_since)
        logging.info("Waiting....")
        print("Waiting...")
        time.sleep(60)


if __name__ == "__main__":
    """
    Run active and pass on desired keywords that tweets will be checked for
    """
    main(KEYWORDS)