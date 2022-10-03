from slack_bolt.adapter.aws_lambda import SlackRequestHandler
import logging

# AWS handler
SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

from slack_bolt import App
from markovbot.markovbot import MarkovBot

import slackfunctions

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# TODO fix this up for S3
mark = MarkovBot(reactions=True)
slackfunctions.bind_events(app, mark)

def lambda_handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)