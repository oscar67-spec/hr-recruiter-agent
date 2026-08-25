"""
Slack Bolt app for HR Recruiter Agent integration.

Features:
- Chat with agent via @mentions or DMs
- Upload resumes for instant screening
- Slash commands for quick actions
- Rich message formatting with interactive buttons
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for importing agent modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests

from agent import build_agent
from slack_integration.slack_handlers import register_handlers
from slack_integration.slack_commands import register_commands

# Initialize Slack app
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)

# Build the HR agent once at startup
hr_agent = build_agent()

# Store agent in app context for handlers to access
app.client.agent = hr_agent

# Register event handlers and commands
register_handlers(app)
register_commands(app)


@app.event("app_mention")
def handle_app_mention(event, say, client):
    """Handle @HRRecruiter mentions in channels."""
    user_id = event.get("user")
    text = event.get("text", "").strip()

    # Remove bot mention from text
    text = text.split(">", 1)[-1].strip() if ">" in text else text

    if not text:
        say(
            text=f"Hi <@{user_id}>! How can I help with your hiring pipeline today?\n\n"
                 "Try asking me to:\n"
                 "• Generate a job posting\n"
                 "• Screen a candidate's resume\n"
                 "• List open positions\n"
                 "• Show top candidates\n"
                 "• Draft an interview email"
        )
        return

    # Show typing indicator
    say(text=f"<@{user_id}> Processing your request...", thread_ts=event.get("ts"))

    # Call the agent
    try:
        result = hr_agent(text)
        response = result.message

        say(
            text=f"<@{user_id}>\n{response}",
            thread_ts=event.get("ts")
        )
    except Exception as e:
        say(
            text=f"<@{user_id}> Sorry, I encountered an error: {str(e)}",
            thread_ts=event.get("ts")
        )


@app.event("message")
def handle_direct_message(event, say, client):
    """Handle direct messages to the bot."""
    # Ignore bot messages and threaded messages
    if event.get("bot_id") or event.get("thread_ts"):
        return

    # Only handle DMs (channel type is 'im')
    if event.get("channel_type") != "im":
        return

    text = event.get("text", "").strip()
    if not text:
        return

    say(text="Thinking...")

    try:
        result = hr_agent(text)
        response = result.message
        say(text=response)
    except Exception as e:
        say(text=f"Sorry, I encountered an error: {str(e)}")


@app.event("file_shared")
def handle_file_upload(event, client, say):
    """Handle resume file uploads."""
    file_id = event.get("file_id")

    try:
        file_info = client.files_info(file=file_id)
        file_data = file_info.get("file", {})
        file_name = file_data.get("name", "resume")
        file_url = file_data.get("url_private")

        headers = {"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"}
        response = requests.get(file_url, headers=headers)

        if response.status_code == 200:
            say(
                text=f"Thanks for uploading `{file_name}`! To screen this resume, please provide:\n"
                     "• Job ID or role name\n"
                     "• Key requirements (e.g., Python, AWS, 5+ years)\n\n"
                     "Example: Screen this resume for job abc123 with requirements: Python, AWS, Docker"
            )
        else:
            say(text="Sorry, I couldn't download the resume file.")

    except Exception as e:
        say(text=f"Error processing file: {str(e)}")


def main():
    """Start the Slack app."""
    if not os.environ.get("SLACK_BOT_TOKEN"):
        print("Error: SLACK_BOT_TOKEN environment variable not set")
        sys.exit(1)

    if not os.environ.get("SLACK_APP_TOKEN"):
        print("Error: SLACK_APP_TOKEN environment variable not set")
        print("Get this from: Slack App Settings > Basic Information > App-Level Tokens")
        sys.exit(1)

    print("HR Recruiter Slack Bot starting...")
    print("Bot is ready to receive messages!")

    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()


if __name__ == "__main__":
    main()
