"""
Script to re-post and re-pin pinned messages that are >=89 days old from every non-archived channel.
This is to make sure pinned messages don't get lost in the free version of slack where messages older
than 90 days are deleted.
"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime, timedelta

# Initialize the Slack API client
slack_token = "<your_slack_api_token>"
client = WebClient(token=slack_token)

# Get a list of all non-archived channels
try:
    channels_response = client.conversations_list(exclude_archived=True)
    channels = channels_response["channels"]
except SlackApiError as e:
    print(f"Error fetching channel list: {e.response['error']}")

# Iterate through each channel and retrieve pinned messages
for channel in channels:
    channel_id = channel["id"]
    try:
        pins_response = client.pins_list(channel=channel_id)
        pins = pins_response["items"]
        for pin in pins:
            # Get the timestamp of the pinned message
            message_ts = float(pin["message"]["ts"])
            
            # Calculate the difference between current time and the pinned message timestamp
            current_time = datetime.now()
            pinned_time = datetime.fromtimestamp(message_ts)
            time_difference = current_time - pinned_time
            
            # Repost the message if it is 89 days or older
            if time_difference >= timedelta(days=89):
                message_text = pin["message"]["text"]
                try:
                    client.chat_postMessage(channel=channel_id, text=message_text)
                    client.pins_add(channel=channel_id, timestamp=pin["message"]["ts"])
                except SlackApiError as e:
                    print(f"Error reposting message: {e.response['error']}")
    except SlackApiError as e:
        print(f"Error fetching pinned messages in channel {channel['name']}: {e.response['error']}")
