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

# Server
PORT = int(os.environ.get("PORT", "8080"))
