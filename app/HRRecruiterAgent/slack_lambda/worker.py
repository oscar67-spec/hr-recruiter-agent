"""
Lambda 2: Slack Worker

Invoked asynchronously by the receiver Lambda.
Calls the deployed AgentCore runtime and posts the response back to Slack.
"""
import json
import os
import urllib.parse
from typing import Optional

import boto3
import requests
try:
    from requests_aws4auth import AWS4Auth  # type: ignore[import]
except ImportError:
    AWS4Auth = None  # type: ignore[assignment,misc]

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
AGENTCORE_RUNTIME_ARN = os.environ["AGENTCORE_RUNTIME_ARN"]
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")


# ── Slack helpers ──────────────────────────────────────────────────────────────

def post_message(channel: str, text: str, thread_ts: Optional[str] = None) -> None:
    """Post a message to a Slack channel or thread."""
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    body: dict = {"channel": channel, "text": text}
    if thread_ts:
        body["thread_ts"] = thread_ts
    try:
        requests.post(
            "https://slack.com/api/chat.postMessage",
            json=body,
            headers=headers,
            timeout=10,
        )
    except Exception as e:
        print(f"[worker] Failed to post to Slack: {e}")


# ── AgentCore helper ───────────────────────────────────────────────────────────

def invoke_agentcore(prompt: str) -> str:
    """Call the deployed AgentCore runtime and return the agent's response."""
    session = boto3.Session(region_name=AWS_REGION)
    creds = session.get_credentials()
    frozen = creds.get_frozen_credentials()

    if AWS4Auth is None:
        raise RuntimeError("requests-aws4auth is not installed")

    auth = AWS4Auth(  # type: ignore[misc]
        frozen.access_key,
        frozen.secret_key,
        AWS_REGION,
        "bedrock-agentcore",
        session_token=frozen.token,
    )

    encoded_arn = urllib.parse.quote(AGENTCORE_RUNTIME_ARN, safe="")
    url = (
        f"https://bedrock-agentcore.{AWS_REGION}.amazonaws.com"
        f"/runtimes/{encoded_arn}/invocations"
    )

    response = requests.post(
        url,
        json={"prompt": prompt},
        auth=auth,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()

    import re

    def extract_text(obj) -> str:
        """Recursively extract text from AgentCore response."""
        if isinstance(obj, str):
            return obj
        if isinstance(obj, dict):
            # Our main.py format
            if "result" in obj:
                return extract_text(obj["result"])
            # Raw AgentCore model format
            if "content" in obj and isinstance(obj["content"], list):
                return extract_text(obj["content"][0])
            if "text" in obj:
                return extract_text(obj["text"])
            # Fallback: dump the whole thing
            return str(obj)
        if isinstance(obj, list) and obj:
            return extract_text(obj[0])
        return str(obj)

    text = extract_text(data)
    # Strip <thinking>...</thinking> tags
    text = re.sub(r"<thinking>.*?</thinking>\s*", "", text, flags=re.DOTALL)
    return text.strip() or "No response from agent."


# ── Main handler ───────────────────────────────────────────────────────────────

def handler(event: dict, context: object) -> None:
    event_type = event.get("type")

    # ── Slack Events API ───────────────────────────────────────────────────────
    if event_type == "event_callback":
        inner = event.get("event", {})
        inner_type = inner.get("type", "")

        # Ignore bot-generated messages (prevent infinite loops)
        if inner.get("bot_id") or inner.get("subtype") == "bot_message":
            return

        text: str = ""
        channel: str = ""
        thread_ts: Optional[str] = None

        if inner_type == "app_mention":
            raw_text: str = inner.get("text", "")
            text = raw_text.split(">", 1)[-1].strip() if ">" in raw_text else raw_text
            channel = inner.get("channel", "")
            thread_ts = inner.get("ts")

        elif inner_type == "message" and inner.get("channel_type") == "im":
            text = inner.get("text", "").strip()
            channel = inner.get("channel", "")
            thread_ts = None

        else:
            return  # Ignore other event types

        if not text:
            post_message(
                channel,
                "Hi! How can I help with your hiring pipeline today?\n\n"
                "Try: _generate a job posting for Senior Engineer_ or "
                "_list all open positions_",
                thread_ts,
            )
            return

        post_message(channel, "_Thinking..._", thread_ts)

        try:
            agent_response = invoke_agentcore(text)
            post_message(channel, agent_response, thread_ts)
        except Exception as e:
            print(f"[worker] AgentCore error: {e}")
            post_message(channel, f"Sorry, I hit an error: {str(e)}", thread_ts)

    # ── Slash command: /hr ─────────────────────────────────────────────────────
    elif event.get("command") == "/hr":
        text = event.get("text", "").strip()
        response_url: str = event.get("response_url", "")
        channel = event.get("channel_id", "")

        if not text:
            if response_url:
                requests.post(
                    response_url,
                    json={"text": "Please include a request after `/hr`. Example: `/hr list all open jobs`"},
                    timeout=10,
                )
            return

        if response_url:
            requests.post(
                response_url,
                json={"text": "_Processing your request..._"},
                timeout=10,
            )

        try:
            agent_response = invoke_agentcore(text)
            if response_url:
                requests.post(
                    response_url,
                    json={"text": agent_response, "replace_original": True},
                    timeout=10,
                )
            else:
                post_message(channel, agent_response)
        except Exception as e:
            print(f"[worker] AgentCore error (slash cmd): {e}")
            if response_url:
                requests.post(
                    response_url,
                    json={"text": f"Sorry, I hit an error: {str(e)}", "replace_original": True},
                    timeout=10,
                )
