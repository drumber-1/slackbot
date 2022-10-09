import boto3
import json
import logging
import os

from slack_bolt import App
from slack_bolt.request import BoltRequest
from markovbot.markovbot import MarkovBot

import slackfunctions
import config

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)
logging.root.setLevel(logging.INFO)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True
)

s3 = boto3.resource("s3")
bucket_name = os.environ.get("BUCKET_NAME")
bucket = s3.Bucket(bucket_name)

keys = ["data/chain.dat", "data/reactions.dat"]
tmp_locations = ["/tmp/chain.dat", "/tmp/reactions.dat"]

def load_data():
    if not os.path.isfile(tmp_locations[0]):
        bucket.download_file(keys[0], tmp_locations[0])
        
    if not os.path.isfile(tmp_locations[1]):
        bucket.download_file(keys[1], tmp_locations[1])
    
    config.mark = MarkovBot(mc_savefile=tmp_locations[0],
                            reaction_savefile=tmp_locations[1],
                            reactions=True)

# Put our data back in S3
# Could optimize this to check if data actually changed ?
def save_data():
    if os.path.isfile(tmp_locations[0]):
        bucket.upload_file(tmp_locations[0], keys[0])
    if os.path.isfile(tmp_locations[0]):
        bucket.upload_file(tmp_locations[1], keys[1])

def on_message(client, message):
    load_data()
    slackfunctions.on_message(client, message)
    save_data()

def on_mention(client, event):
    load_data()
    slackfunctions.on_mention(client, event)
    # save_data() # Don't need to save on mentions
    
def on_reaction(client, event):
    load_data()
    slackfunctions.on_reaction(client, event)
    save_data()
    
def lambda_handler(event, context):
    body_str = event["Records"][0]["body"]
    slack_event = json.loads(body_str)
    
    logging.info(event)
    
    if not "type" in slack_event:
        logging.error("No type in event")
        logging.error(slack_event)
    elif slack_event["type"] == "message":
         logging.info("message")
         on_message(app.client, slack_event)
    elif slack_event["type"] == "app_mention":
        logging.info("mention")
        on_mention(app.client, slack_event)
    elif slack_event["type"] == "reaction_added":
        logging.info("reaction")
        on_reaction(app.client, slack_event)
    else:
        logging.error("Unhandled event type {}".format(slack_event["type"]))
        logging.error(slack_event)
    
    return {
        'statusCode': 200,
        'body': 'We did it!'
    }
    