"""
Comprehensive tool test suite — tests all 23 tools directly against real credentials.

Run from app/HRRecruiterAgent/:
    python test_tools.py

Results are printed as PASS / FAIL / SKIP with a summary at the end.
"""
from __future__ import annotations

import os
import sys
import traceback
import time
from pathlib import Path

# ── Load .env before importing anything else ──────────────────────────────────
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())
    print(f"Loaded .env from {env_path}\n")
else:
    print("WARNING: .env not found — some tests will be skipped.\n")

# ── Ensure local modules are importable ───────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

# ── Colour helpers ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

results: list[tuple[str, str, str]] = []   # (tool_name, status, detail)

def run(tool_name: str, fn, *args, **kwargs):
    """Execute fn(*args, **kwargs) and record PASS / FAIL."""
    try:
        out = fn(*args, **kwargs)
        # A tool that returns an error string (not raises) still counts as a failure
        if isinstance(out, str) and (
            "not configured" in out.lower()
            or "error" in out.lower()[:60]
            or out.startswith("Error ")
        ):
            # Flag as WARN — tool ran but returned a soft error
            results.append((tool_name, "WARN", out[:120]))
            print(f"  {YELLOW}WARN{RESET}  {tool_name}")
            print(f"         {out[:120]}")
        else:
            results.append((tool_name, "PASS", str(out)[:120]))
            print(f"  {GREEN}PASS{RESET}  {tool_name}")
            print(f"         {str(out)[:120]}")
    except Exception as exc:  # noqa: BLE001
        tb = traceback.format_exc().strip().splitlines()[-1]
        results.append((tool_name, "FAIL", tb))
        print(f"  {RED}FAIL{RESET}  {tool_name}")
        print(f"         {tb}")
    time.sleep(0.3)   # small delay to avoid rate limits


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 1 — Core HR Tools  (tools.py)
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 65)
print("GROUP 1 — Core HR Tools (Bedrock + S3)")
print("=" * 65)

from tools import (
    generate_job_posting,
    save_job_posting,
    list_job_postings,
    screen_resume,
    save_candidate,
    list_candidates,
    draft_interview_email,
)

# 1. generate_job_posting
run(
    "generate_job_posting",
    generate_job_posting,
    role="Software Engineer",
    department="Engineering",
    requirements="Python, AWS, REST APIs",
    location="Remote",
    employment_type="Full-time",
)

# 2. save_job_posting
run(
    "save_job_posting",
    save_job_posting,
    role="Software Engineer",
    department="Engineering",
    description="Test job description for automated testing.",
    location="Remote",
    employment_type="Full-time",
)

# 3. list_job_postings
run("list_job_postings", list_job_postings)

# 4. screen_resume
SAMPLE_RESUME = """
John Smith | john.smith@example.com | (555) 123-4567
LinkedIn: linkedin.com/in/johnsmith

EXPERIENCE
Senior Software Engineer — Acme Corp (2021-2026)
  - Built microservices in Python and FastAPI deployed on AWS Lambda
  - Designed REST APIs serving 50M+ requests/day
  - Led team of 4 engineers, improved CI/CD pipeline reducing deploy time by 40%

Software Engineer — StartupXYZ (2019-2021)
  - Full-stack development with React and Node.js
  - Migrated monolith to Kubernetes-based microservices

EDUCATION
B.Sc. Computer Science — State University (2019)

SKILLS
Python, FastAPI, AWS (Lambda, S3, DynamoDB, EC2), REST APIs, Docker, Kubernetes, React
"""

run(
    "screen_resume",
    screen_resume,
    candidate_name="John Smith",
    candidate_email="john.smith@example.com",
    resume_text=SAMPLE_RESUME,
    job_id="TEST-001",
    role="Software Engineer",
    key_requirements="Python, AWS, REST APIs",
)

# 5. save_candidate
run(
    "save_candidate",
    save_candidate,
    candidate_name="John Smith",
    candidate_email="john.smith@example.com",
    job_id="TEST-001",
    role="Software Engineer",
    score=82,
    strengths="5 years Python, AWS Lambda experience, team lead",
    gaps="No Kubernetes at scale mentioned",
    recommendation="Advance",
    summary="Strong senior engineer with solid AWS and Python background.",
)

# 6. list_candidates
run("list_candidates", list_candidates)

# 7. draft_interview_email
run(
    "draft_interview_email",
    draft_interview_email,
    candidate_name="John Smith",
    candidate_email="john.smith@example.com",
    role="Software Engineer",
    department="Engineering",
    interviewer_name="Alice Johnson",
    company_name="BuildItt",
    interview_format="video call (Google Meet)",
    date_options="Monday to Wednesday, 10am-4pm EST next week",
)


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 2 — Google Drive Tools  (google_tools.py)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("GROUP 2 — Google Drive Tools")
print("=" * 65)

from google_tools import (
    read_resume_from_drive,
    save_document_to_drive,
    list_drive_files,
)

# 8. save_document_to_drive  (do this first so list_drive_files has something)
run(
    "save_document_to_drive",
    save_document_to_drive,
    filename="TestJobDescription.txt",
    content="This is a test job description saved by the automated test suite.",
    folder_name="HR Recruiter",
)

# 9. list_drive_files
run(
    "list_drive_files",
    list_drive_files,
    folder_name="HR Recruiter",
)

# 10. read_resume_from_drive — look for anything with "resume" in name
run(
    "read_resume_from_drive",
    read_resume_from_drive,
    file_name="resume",
)


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 3 — Gmail Tools
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("GROUP 3 — Gmail Tools")
print("=" * 65)

from google_tools import send_email_now, list_unread_emails

# 11. list_unread_emails
run(
    "list_unread_emails",
    list_unread_emails,
    search_query="is:unread",
    max_results=5,
)

# 12. send_email_now — sends to self (safe for testing)
MY_EMAIL = os.environ.get("GOOGLE_TEST_EMAIL", "chidiadi.works@gmail.com")
run(
    "send_email_now",
    send_email_now,
    to_email=MY_EMAIL,
    to_name="Test Recipient",
    subject="[HR Agent Test] Tool test email",
    body=(
        "This is an automated test email sent by the HR Recruiter Agent test suite.\n"
        "If you received this, the send_email_now tool is working correctly."
    ),
)


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 4 — Google Calendar Tools
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("GROUP 4 — Google Calendar Tools")
print("=" * 65)

from google_tools import schedule_interview, check_availability

INTERVIEWER_EMAIL = MY_EMAIL   # use same account for testing

# 13. check_availability
run(
    "check_availability",
    check_availability,
    interviewer_email=INTERVIEWER_EMAIL,
    date="2026-09-15",
)

# 14. schedule_interview — creates a real calendar event
run(
    "schedule_interview",
    schedule_interview,
    candidate_name="Test Candidate",
    candidate_email=MY_EMAIL,
    interviewer_email=INTERVIEWER_EMAIL,
    role="Software Engineer",
    date_time_iso="2026-09-16T14:00:00",
    duration_minutes=45,
    notes="Automated test interview — please delete after verifying.",
)


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 5 — Google Forms + Sheets Tools
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("GROUP 5 — Google Forms + Sheets Tools")
print("=" * 65)

from google_tools import create_job_application_form, list_form_responses, read_sheet

# 15. create_job_application_form
created_form_id = None
def _create_form():
    global created_form_id
    out = create_job_application_form(
        job_title="Software Engineer (Test)",
        job_description="Automated test form — please delete after testing.",
        custom_questions=["How did you hear about this role?"],
    )
    # Try to extract form_id for subsequent list_form_responses test
    for line in out.splitlines():
        if line.strip().startswith("Form ID"):
            created_form_id = line.split(":")[-1].strip()
    return out

run("create_job_application_form", _create_form)

# 16. list_form_responses — use the form just created (or a placeholder)
def _list_responses():
    form_id = created_form_id or os.environ.get("TEST_FORM_ID", "")
    if not form_id:
        return "Skipped: no form ID available (create_job_application_form may have failed)"
    return list_form_responses(form_id=form_id, max_responses=5)

run("list_form_responses", _list_responses)

# 17. read_sheet — use TEST_SPREADSHEET_ID env var if available, else skip gracefully
def _read_sheet():
    spreadsheet_id = os.environ.get("TEST_SPREADSHEET_ID", "")
    if not spreadsheet_id:
        return "Skipped: set TEST_SPREADSHEET_ID in .env to test this tool"
    return read_sheet(spreadsheet_id=spreadsheet_id, sheet_name="Sheet1", max_rows=10)

run("read_sheet", _read_sheet)


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 6 — Zoho Recruit Tools  (ats_tools.py)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("GROUP 6 — Zoho Recruit Tools")
print("=" * 65)

from ats_tools import list_zoho_jobs, get_zoho_candidates, update_zoho_candidate

# 18. list_zoho_jobs
zoho_job_id = None
def _list_zoho_jobs():
    global zoho_job_id
    out = list_zoho_jobs(status="open")
    # Try to extract first job ID for follow-up tests
    for line in out.splitlines():
        if "Job ID" in line:
            zoho_job_id = line.split(":")[-1].strip()
            break
    return out

run("list_zoho_jobs", _list_zoho_jobs)

# 19. get_zoho_candidates
zoho_candidate_id = None
def _get_zoho_candidates():
    global zoho_candidate_id
    out = get_zoho_candidates(max_results=5)
    for line in out.splitlines():
        if "Candidate ID" in line:
            zoho_candidate_id = line.split(":")[-1].strip()
            break
    return out

run("get_zoho_candidates", _get_zoho_candidates)

# 20. update_zoho_candidate — only run if we got a real candidate ID
def _update_zoho_candidate():
    cid = zoho_candidate_id or os.environ.get("TEST_ZOHO_CANDIDATE_ID", "")
    if not cid:
        return "Skipped: no candidate ID available from get_zoho_candidates"
    return update_zoho_candidate(
        candidate_id=cid,
        stage="Screening",
        notes="AI test note: Automated test run — status unchanged.",
        score=75,
    )

run("update_zoho_candidate", _update_zoho_candidate)


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 7 — Workable Tools  (ats_tools.py)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("GROUP 7 — Workable Tools")
print("=" * 65)

from ats_tools import list_workable_jobs, get_workable_candidates, update_workable_candidate

# 21. list_workable_jobs
workable_shortcode = None
def _list_workable_jobs():
    global workable_shortcode
    out = list_workable_jobs(state="published")
    for line in out.splitlines():
        if "Shortcode" in line:
            workable_shortcode = line.split(":")[-1].strip()
            break
    return out

run("list_workable_jobs", _list_workable_jobs)

# 22. get_workable_candidates
workable_candidate_id = None
def _get_workable_candidates():
    global workable_candidate_id
    sc = workable_shortcode or ""
    out = get_workable_candidates(job_shortcode=sc, max_results=5)
    for line in out.splitlines():
        if "Candidate ID" in line:
            workable_candidate_id = line.split(":")[-1].strip()
            break
    return out

run("get_workable_candidates", _get_workable_candidates)

# 23. update_workable_candidate — comment only (safe, non-destructive)
def _update_workable_candidate():
    cid = workable_candidate_id or os.environ.get("TEST_WORKABLE_CANDIDATE_ID", "")
    sc  = workable_shortcode or os.environ.get("TEST_WORKABLE_SHORTCODE", "")
    if not cid or not sc:
        return "Skipped: need both candidate ID and job shortcode from previous steps"
    return update_workable_candidate(
        candidate_id=cid,
        job_shortcode=sc,
        action="comment",
        notes="AI test note: Automated test run.",
        score=75,
    )

run("update_workable_candidate", _update_workable_candidate)


# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("SUMMARY")
print("=" * 65)

passed  = [r for r in results if r[1] == "PASS"]
warned  = [r for r in results if r[1] == "WARN"]
failed  = [r for r in results if r[1] == "FAIL"]
skipped = [r for r in results if "kipped" in r[2]]

print(f"  {GREEN}PASS{RESET}  : {len(passed)}")
print(f"  {YELLOW}WARN{RESET}  : {len(warned)}  (ran but returned a soft-error string)")
print(f"  {RED}FAIL{RESET}  : {len(failed)}  (raised an exception)")
print(f"  SKIP  : {len(skipped)}  (no data to test against)")
print(f"  TOTAL : {len(results)}")

if warned:
    print(f"\n{YELLOW}WARN details:{RESET}")
    for name, _, detail in warned:
        print(f"  {name}: {detail}")

if failed:
    print(f"\n{RED}FAIL details:{RESET}")
    for name, _, detail in failed:
        print(f"  {name}: {detail}")

if skipped:
    print(f"\nSKIP details:")
    for name, _, detail in skipped:
        print(f"  {name}: {detail}")

print()
sys.exit(1 if failed else 0)
