"""
Strands @tool definitions for the HR Recruiter Agent.

Tools:
  1. generate_job_posting   – draft a full JD from a role brief (calls Bedrock)
  2. save_job_posting       – persist a JD to S3 and return job_id
  3. list_job_postings      – show all open roles from S3
  4. screen_resume          – score and summarise a candidate vs. a JD (calls Bedrock)
  5. save_candidate         – store a screened candidate record to S3
  6. list_candidates        – dashboard: filter by role / min score
  7. draft_interview_email  – write a ready-to-send invite email (calls Bedrock)
"""
from __future__ import annotations

import json
from typing import Optional

import boto3
from strands import tool  # type: ignore[import]

import storage
from config import AWS_REGION, BEDROCK_MODEL_ID


# ---------------------------------------------------------------------------
# Internal helper – thin Bedrock inference call
# ---------------------------------------------------------------------------

def _llm(prompt: str) -> str:
    """Call Nova Lite (or configured model) on Bedrock and return the text."""
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    body = {
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"maxTokens": 1024, "temperature": 0.4},
    }
    resp = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(resp["body"].read())
    return result["output"]["message"]["content"][0]["text"].strip()


# ---------------------------------------------------------------------------
# 1. Generate job posting
# ---------------------------------------------------------------------------

@tool
def generate_job_posting(
    role: str,
    department: str,
    requirements: str,
    location: str = "Remote",
    employment_type: str = "Full-time",
) -> str:
    """
    Draft a complete, inclusive job description using AI.

    Args:
        role: Job title (e.g. "Senior Software Engineer")
        department: Department hiring for this role (e.g. "Engineering")
        requirements: Comma-separated key skills or qualifications required
        location: Work location (default "Remote")
        employment_type: Employment type, e.g. Full-time, Part-time, Contract

    Returns:
        A structured job description ready to publish.
    """
    prompt = (
        "You are an expert HR professional. "
        "Write a clear, engaging, and inclusive job description.\n\n"
        f"Role: {role}\n"
        f"Department: {department}\n"
        f"Location: {location}\n"
        f"Employment Type: {employment_type}\n"
        f"Key Requirements: {requirements}\n\n"
        "Format the JD with these sections:\n"
        "- About the Role (2-3 sentences)\n"
        "- Key Responsibilities (5-7 bullet points)\n"
        "- Required Qualifications (from the requirements provided)\n"
        "- Preferred Qualifications (2-3 nice-to-haves you infer from the role)\n"
        "- What We Offer (competitive salary, growth, remote options, etc.)\n\n"
        "Keep it professional and welcoming. Avoid gender-coded language."
    )
    return _llm(prompt)


# ---------------------------------------------------------------------------
# 2. Save job posting
# ---------------------------------------------------------------------------

@tool
def save_job_posting(
    role: str,
    department: str,
    description: str,
    location: str = "Remote",
    employment_type: str = "Full-time",
) -> str:
    """
    Save a job posting to S3 and return its job ID.

    Args:
        role: Job title
        department: Department name
        description: Full job description text
        location: Work location
        employment_type: Employment type

    Returns:
        Confirmation message with the assigned job_id.
    """
    record = {
        "role": role,
        "department": department,
        "description": description,
        "location": location,
        "employment_type": employment_type,
        "status": "open",
    }
    job_id = storage.save_job_posting(record)
    return (
        f"Job posting saved.\n"
        f"Job ID: {job_id}\n"
        f"Role: {role} | Department: {department} | Location: {location}"
    )


# ---------------------------------------------------------------------------
# 3. List job postings
# ---------------------------------------------------------------------------

@tool
def list_job_postings() -> str:
    """
    Retrieve all job postings from S3.

    Returns:
        A formatted summary of all job postings with their IDs and status.
    """
    postings = storage.list_job_postings()
    if not postings:
        return "No job postings found. Use generate_job_posting and save_job_posting to create one."

    lines = [f"Found {len(postings)} job posting(s):\n"]
    for p in postings:
        lines.append(
            f"  Job ID : {p.get('job_id', 'N/A')}\n"
            f"  Role   : {p.get('role', 'N/A')}\n"
            f"  Dept   : {p.get('department', 'N/A')}\n"
            f"  Status : {p.get('status', 'open')}\n"
            f"  Created: {p.get('created_at', 'N/A')[:10]}\n"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 4. Screen resume
# ---------------------------------------------------------------------------

@tool
def screen_resume(
    candidate_name: str,
    candidate_email: str,
    resume_text: str,
    job_id: str,
    role: str,
    key_requirements: str,
) -> str:
    """
    Evaluate a candidate's resume against job requirements using AI.
    Produces a score from 0-100 and a structured assessment.

    Args:
        candidate_name: Full name of the applicant
        candidate_email: Email address of the applicant
        resume_text: Full text content of the resume / CV
        job_id: The job_id the candidate is applying for
        role: The role title
        key_requirements: Comma-separated list of required skills / qualifications

    Returns:
        A screening report with score, strengths, gaps, and recommendation.
    """
    # Truncate resume to keep token cost low
    truncated_resume = resume_text[:3000]

    prompt = (
        f"You are a senior HR recruiter. Evaluate this resume for the role of {role}.\n\n"
        f"Key Requirements: {key_requirements}\n\n"
        f"Resume:\n{truncated_resume}\n\n"
        "Provide a structured assessment with exactly these fields:\n"
        "SCORE: (integer 0-100)\n"
        "STRENGTHS:\n- (bullet 1)\n- (bullet 2)\n- (bullet 3)\n"
        "GAPS:\n- (bullet 1)\n- (bullet 2)\n"
        "RECOMMENDATION: (Advance / Hold / Reject)\n"
        "SUMMARY: (one sentence for the hiring manager)\n\n"
        "Be objective and concise."
    )
    assessment = _llm(prompt)
    return (
        f"Screening Report for {candidate_name} ({candidate_email})\n"
        f"Applying for: {role} (Job ID: {job_id})\n"
        f"{'=' * 60}\n"
        f"{assessment}"
    )


# ---------------------------------------------------------------------------
# 5. Save candidate
# ---------------------------------------------------------------------------

@tool
def save_candidate(
    candidate_name: str,
    candidate_email: str,
    job_id: str,
    role: str,
    score: int,
    strengths: str,
    gaps: str,
    recommendation: str,
    summary: str,
) -> str:
    """
    Save a screened candidate record to S3.

    Args:
        candidate_name: Full name of the applicant
        candidate_email: Email address
        job_id: Job posting ID they applied to
        role: Role title
        score: Screening score 0-100
        strengths: Key strengths identified in screening
        gaps: Gaps or concerns identified
        recommendation: Advance / Hold / Reject
        summary: One-line hiring manager summary

    Returns:
        Confirmation with the candidate_id assigned.
    """
    record = {
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "job_id": job_id,
        "role": role,
        "score": score,
        "strengths": strengths,
        "gaps": gaps,
        "recommendation": recommendation,
        "summary": summary,
        "status": "screened",
    }
    candidate_id = storage.save_candidate(record)
    return (
        f"Candidate saved.\n"
        f"Candidate ID  : {candidate_id}\n"
        f"Name          : {candidate_name}\n"
        f"Score         : {score}/100\n"
        f"Recommendation: {recommendation}"
    )


# ---------------------------------------------------------------------------
# 6. List candidates
# ---------------------------------------------------------------------------

@tool
def list_candidates(
    job_id: Optional[str] = None,
    min_score: int = 0,
) -> str:
    """
    Show a ranked dashboard of candidates, optionally filtered by role and score.

    Args:
        job_id: Filter by a specific job posting ID (leave empty for all roles)
        min_score: Only show candidates at or above this score (0-100)

    Returns:
        Ranked table of candidates with scores and recommendations.
    """
    candidates = storage.list_candidates(job_id=job_id, min_score=min_score)
    if not candidates:
        filter_note = ""
        if job_id:
            filter_note += f" for job {job_id}"
        if min_score:
            filter_note += f" with score >= {min_score}"
        return f"No candidates found{filter_note}."

    header = (
        f"{'#':<4} {'Name':<25} {'Role':<28} "
        f"{'Score':<7} {'Rec':<10} Email"
    )
    separator = "-" * 95
    lines = [
        f"Candidate Dashboard — {len(candidates)} result(s)\n",
        header,
        separator,
    ]
    for i, c in enumerate(candidates, 1):
        lines.append(
            f"{i:<4} {c.get('candidate_name', 'N/A'):<25} "
            f"{c.get('role', 'N/A'):<28} "
            f"{c.get('score', 0):<7} "
            f"{c.get('recommendation', 'N/A'):<10} "
            f"{c.get('candidate_email', 'N/A')}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 7. Draft interview email
# ---------------------------------------------------------------------------

@tool
def draft_interview_email(
    candidate_name: str,
    candidate_email: str,
    role: str,
    department: str,
    interviewer_name: str,
    company_name: str = "Our Company",
    interview_format: str = "video call (Google Meet or Zoom)",
    date_options: str = "Monday to Friday, 9am to 5pm EST next week",
) -> str:
    """
    Write a professional interview invitation email ready to send or copy-paste.

    Args:
        candidate_name: Applicant full name
        candidate_email: Applicant email address (shown in output header)
        role: Role they applied for
        department: Hiring department
        interviewer_name: Name of the interviewer / hiring manager
        company_name: Company name
        interview_format: Format details, e.g. "video call (Zoom)"
        date_options: Available time slots to offer the candidate

    Returns:
        Complete interview invitation email with subject line.
    """
    prompt = (
        "Write a warm, professional interview invitation email.\n\n"
        f"Candidate: {candidate_name}\n"
        f"Role: {role}\n"
        f"Department: {department}\n"
        f"Interviewer: {interviewer_name}\n"
        f"Company: {company_name}\n"
        f"Format: {interview_format}\n"
        f"Available slots: {date_options}\n\n"
        "Include:\n"
        "- Subject line (start with 'Subject:')\n"
        "- Warm greeting\n"
        "- Congratulations on progressing to the interview stage\n"
        "- Interview format and estimated duration (45 minutes)\n"
        "- 2-3 specific time slot options\n"
        "- Brief agenda: intro, role discussion, Q&A\n"
        "- What to prepare\n"
        "- Contact info for scheduling\n"
        "- Professional sign-off from the interviewer\n\n"
        "Tone: warm, professional, and encouraging."
    )
    email_draft = _llm(prompt)
    return (
        f"To: {candidate_name} <{candidate_email}>\n"
        f"{'=' * 60}\n"
        f"{email_draft}"
    )
