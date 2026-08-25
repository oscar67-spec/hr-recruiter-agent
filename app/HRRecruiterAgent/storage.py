"""
S3-backed storage helpers for the HR Recruiter Agent.

Data layout in S3:
  {prefix}/jobs/{job_id}.json          — job posting records
  {prefix}/candidates/{job_id}/{candidate_id}.json  — candidate records
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import boto3
from botocore.exceptions import ClientError

from config import AWS_REGION, S3_BUCKET_NAME, JOB_POSTINGS_PREFIX, CANDIDATES_PREFIX


def _s3():
    return boto3.client("s3", region_name=AWS_REGION)


# ---------------------------------------------------------------------------
# Job postings
# ---------------------------------------------------------------------------

def save_job_posting(data: dict[str, Any]) -> str:
    """
    Persist a job posting to S3.
    Adds a generated job_id and created_at if not present.
    Returns the job_id.
    """
    if "job_id" not in data:
        data["job_id"] = str(uuid.uuid4())[:8]
    if "created_at" not in data:
        data["created_at"] = datetime.now(timezone.utc).isoformat()

    key = f"{JOB_POSTINGS_PREFIX}/{data['job_id']}.json"
    _s3().put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=json.dumps(data, indent=2),
        ContentType="application/json",
    )
    return data["job_id"]


def get_job_posting(job_id: str) -> dict[str, Any] | None:
    """Fetch a single job posting by job_id. Returns None if not found."""
    key = f"{JOB_POSTINGS_PREFIX}/{job_id}.json"
    try:
        resp = _s3().get_object(Bucket=S3_BUCKET_NAME, Key=key)
        return json.loads(resp["Body"].read())
    except ClientError as e:
        if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
            return None
        raise


def list_job_postings() -> list[dict[str, Any]]:
    """Return all job postings, sorted by created_at descending."""
    prefix = f"{JOB_POSTINGS_PREFIX}/"
    paginator = _s3().get_paginator("list_objects_v2")
    postings = []
    for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix):
        for obj in page.get("Contents", []):
            try:
                resp = _s3().get_object(Bucket=S3_BUCKET_NAME, Key=obj["Key"])
                postings.append(json.loads(resp["Body"].read()))
            except ClientError:
                continue
    return sorted(postings, key=lambda x: x.get("created_at", ""), reverse=True)


# ---------------------------------------------------------------------------
# Candidates
# ---------------------------------------------------------------------------

def save_candidate(data: dict[str, Any]) -> str:
    """
    Persist a candidate record to S3 under their job_id folder.
    Returns the candidate_id.
    """
    if "candidate_id" not in data:
        data["candidate_id"] = str(uuid.uuid4())[:8]
    if "created_at" not in data:
        data["created_at"] = datetime.now(timezone.utc).isoformat()

    job_id = data.get("job_id", "unassigned")
    key = f"{CANDIDATES_PREFIX}/{job_id}/{data['candidate_id']}.json"
    _s3().put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=json.dumps(data, indent=2),
        ContentType="application/json",
    )
    return data["candidate_id"]


def get_candidate(job_id: str, candidate_id: str) -> dict[str, Any] | None:
    """Fetch a single candidate record. Returns None if not found."""
    key = f"{CANDIDATES_PREFIX}/{job_id}/{candidate_id}.json"
    try:
        resp = _s3().get_object(Bucket=S3_BUCKET_NAME, Key=key)
        return json.loads(resp["Body"].read())
    except ClientError as e:
        if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
            return None
        raise


def list_candidates(
    job_id: str | None = None,
    min_score: int = 0,
) -> list[dict[str, Any]]:
    """
    List candidates, optionally filtered by job_id and minimum score.
    Returns list sorted by score descending.
    """
    prefix = f"{CANDIDATES_PREFIX}/"
    if job_id:
        prefix = f"{CANDIDATES_PREFIX}/{job_id}/"

    paginator = _s3().get_paginator("list_objects_v2")
    candidates = []
    for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix):
        for obj in page.get("Contents", []):
            try:
                resp = _s3().get_object(Bucket=S3_BUCKET_NAME, Key=obj["Key"])
                record = json.loads(resp["Body"].read())
                if record.get("score", 0) >= min_score:
                    candidates.append(record)
            except ClientError:
                continue

    return sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)
