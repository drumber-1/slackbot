import os
import logging

from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from markovbot.markovbot import MarkovBot

import slackfunctions

# AWS handler
SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True
)

# TODO fix this up for S3
mark = MarkovBot(mc_savefile="/tmp/chain.dat",
                 reaction_savefile="/tmp/reactions.dat",
                 reactions=True)
slackfunctions.bind_events(app, mark)

def lambda_handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)