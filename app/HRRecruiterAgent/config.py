"""
Configuration for the HR Recruiter Agent.
All settings are read from environment variables with sensible defaults.
"""
import os

# AWS / Bedrock
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
BEDROCK_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "amazon.nova-lite-v1:0",  # cheapest Nova model - very low cost
)

# S3 storage
S3_BUCKET_NAME = os.environ.get("HR_S3_BUCKET", "hr-recruiter-agent-data")
S3_PREFIX = os.environ.get("HR_S3_PREFIX", "hr-agent")

# Prefixes inside the bucket
JOB_POSTINGS_PREFIX = f"{S3_PREFIX}/jobs"
CANDIDATES_PREFIX = f"{S3_PREFIX}/candidates"

# Memory
# Name of the AgentCore Memory resource declared in agentcore.json.
# At runtime the agent discovers the memory ID by this name via the control-plane API.
MEMORY_NAME = os.environ.get("MEMORY_NAME", "HRRecruiterMemory")

# ── Google OAuth2 ────────────────────────────────────────────────────────────
# Run setup/google_auth.py once to obtain these values.
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", "")

# ── ATS Credentials ──────────────────────────────────────────────────────────
# Zoho Recruit
ZOHO_CLIENT_ID = os.environ.get("ZOHO_CLIENT_ID", "")
ZOHO_CLIENT_SECRET = os.environ.get("ZOHO_CLIENT_SECRET", "")
ZOHO_REFRESH_TOKEN = os.environ.get("ZOHO_REFRESH_TOKEN", "")

# Workable
WORKABLE_API_KEY = os.environ.get("WORKABLE_API_KEY", "")
WORKABLE_SUBDOMAIN = os.environ.get("WORKABLE_SUBDOMAIN", "")

# Server
PORT = int(os.environ.get("PORT", "8080"))
