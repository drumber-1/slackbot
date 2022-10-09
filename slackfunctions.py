import os
import re

import config

re_mention = re.compile("<[@!].+>")

def on_message(client, message):
    # Ignore other bots
    if "bot_id" in message:
        return
    
    # Ignore messages with mentions in them
    m = re_mention.search(message["text"])
    if m is not None:
        return

    response = config.mark.on_message(message["text"])
    process_response(response, client, message["channel"], message["ts"])

def on_mention(client, event):
    response = config.mark.on_mention()
    process_response(response, client, event["channel"], event["ts"])

def on_reaction(client, event):
    item_user = event["item_user"]
    self_user = client.auth_test()["user_id"]

    reacted_message = client.conversations_history(channel=event["item"]["channel"],
                                                oldest=event["item"]["ts"],
                                                latest=event["item"]["ts"],
                                                inclusive=True,
                                                limit=1)

    response = config.mark.on_reaction(event["reaction"],
                                       float(event["event_ts"]),
                                       reacted_message["messages"][0]["text"],
                                       float(event["item"]["ts"]),
                                       item_user == self_user)

    process_response(response, client, event["item"]["channel"], event["item"]["ts"])

def process_response(response, client, channel, timestamp):
    if response["message"]:
        client.chat_postMessage(channel=channel, text=response["message"])
    if response["reaction"]:
        client.reactions_add(channel=channel, name=response["reaction"], timestamp=timestamp)

def bind_events(app, mark):
    config.mark = mark
    app.message("")(on_message)
    app.event("app_mention")(on_mention)
    app.event("reaction_added")(on_reaction)
