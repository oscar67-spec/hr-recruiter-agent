"""
Lambda 1: Slack Receiver

Receives events from Slack via API Gateway.
Verifies the signature, handles URL verification,
then async-invokes the worker Lambda and immediately returns 200.
"""
import json
import hmac
import hashlib
import os
import boto3


def verify_slack_signature(body: str, headers: dict) -> bool:
    signing_secret = os.environ["SLACK_SIGNING_SECRET"].encode()
    timestamp = (
        headers.get("x-slack-request-timestamp")
        or headers.get("X-Slack-Request-Timestamp", "")
    )
    slack_sig = (
        headers.get("x-slack-signature")
        or headers.get("X-Slack-Signature", "")
    )
    if not timestamp or not slack_sig:
        return False
    base = f"v0:{timestamp}:{body}".encode()
    computed = "v0=" + hmac.new(signing_secret, base, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, slack_sig)


def handler(event, context):
    body = event.get("body", "")
    headers = event.get("headers", {})

    # Verify Slack signature
    if not verify_slack_signature(body, headers):
        return {"statusCode": 401, "body": "Unauthorized"}

    try:
        payload = json.loads(body)
    except Exception:
        return {"statusCode": 400, "body": "Bad Request"}

    # Slack URL verification challenge (one-time setup)
    if payload.get("type") == "url_verification":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"challenge": payload["challenge"]}),
        }

    # Async invoke the worker Lambda — do NOT wait for it
    lambda_client = boto3.client("lambda", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    lambda_client.invoke(
        FunctionName=os.environ["WORKER_FUNCTION_NAME"],
        InvocationType="Event",          # fire-and-forget
        Payload=json.dumps(payload).encode(),
    )

    # Return 200 to Slack immediately (within 3-second window)
    return {"statusCode": 200, "body": ""}
