from slack_bolt.adapter.aws_lambda import SlackRequestHandler
import logging

# AWS handler
SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

from main import app
from main import mark

# TODO fix this up for S3
mark = MarkovBot(reactions=True)

def lambda_handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)