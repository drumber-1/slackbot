import os

from slack_bolt import App
from markovbot.markovbot import MarkovBot

import slackfunctions

# Start bot for local testing
if __name__ == "__main__":
    app = App(
        token=os.environ.get("SLACK_BOT_TOKEN"),
        signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
    )

    mark = MarkovBot(reactions=True)
    slackfunctions = slackfunctions.bind_events(app, mark)
    app.start(port=int(os.environ.get("PORT", 3000)))
