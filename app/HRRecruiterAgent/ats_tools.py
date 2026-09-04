"""
ATS (Applicant Tracking System) integrations for the HR Recruiter Agent.

Supports two platforms:

  Zoho Recruit  — recruit.zoho.com/recruit/v2
  Workable      — {subdomain}.workable.com/spi/v3

Each platform exposes:
  - list jobs / open roles
  - list applications / candidates
  - update application status (advance, reject, add notes)

Setup:
  Add the relevant keys to app/HRRecruiterAgent/.env:
    ZOHO_CLIENT_ID=...
    ZOHO_CLIENT_SECRET=...
    ZOHO_REFRESH_TOKEN=...
    WORKABLE_API_KEY=...
    WORKABLE_SUBDOMAIN=...    (e.g. "builditt" from builditt.workable.com)
"""
from __future__ import annotations

import os
from typing import Optional

import requests
from strands import tool  # type: ignore[import]


# ---------------------------------------------------------------------------
# Zoho Recruit helpers
# ---------------------------------------------------------------------------

def _zoho_access_token() -> str:
    """Exchange the stored refresh token for a fresh Zoho access token."""
    client_id = os.environ.get("ZOHO_CLIENT_ID", "")
    client_secret = os.environ.get("ZOHO_CLIENT_SECRET", "")
    refresh_token = os.environ.get("ZOHO_REFRESH_TOKEN", "")

    if not all([client_id, client_secret, refresh_token]):
        raise RuntimeError(
            "Zoho credentials not configured.  "
            "Set ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN in .env."
        )

    resp = requests.post(
        "https://accounts.zoho.com/oauth/v2/token",
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    token = data.get("access_token", "")
    if not token:
        raise RuntimeError(f"Zoho token refresh failed: {data}")
    return token


def _zoho_headers() -> dict:
    return {
        "Authorization": f"Zoho-oauthtoken {_zoho_access_token()}",
        "Content-Type": "application/json",
    }


ZOHO_BASE = "https://recruit.zoho.com/recruit/v2"


# ---------------------------------------------------------------------------
# Workable helpers
# ---------------------------------------------------------------------------

def _workable_headers() -> dict:
    key = os.environ.get("WORKABLE_API_KEY", "")
    if not key:
        raise RuntimeError(
            "WORKABLE_API_KEY not set in .env.  "
            "Generate one in Workable → Settings → Integrations → API Access Tokens."
        )
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def _workable_base() -> str:
    subdomain = os.environ.get("WORKABLE_SUBDOMAIN", "")
    if not subdomain:
        raise RuntimeError(
            "WORKABLE_SUBDOMAIN not set in .env.  "
            "It is the first part of your Workable URL, e.g. 'builditt' from builditt.workable.com."
        )
    return f"https://{subdomain}.workable.com/spi/v3"


# ===========================================================================
# ZOHO RECRUIT TOOLS
# ===========================================================================

@tool
def list_zoho_jobs(status: str = "open") -> str:
    """
    List all job openings in Zoho Recruit.

    Args:
        status: Filter by status — "open", "closed", or "on_hold"
                (default: "open")

    Returns:
        List of job openings with IDs, titles, departments, and location.
    """
    try:
        params = {"criteria": f"(Job_Status:equals:{status})"}
        resp = requests.get(
            f"{ZOHO_BASE}/JobOpenings/search",
            headers=_zoho_headers(),
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        jobs = data.get("data", [])

        if not jobs:
            return f"No {status} job openings found in Zoho Recruit."

        lines = [f"Zoho Recruit — Job Openings ({status}) — {len(jobs)} total:\n"]
        for j in jobs:
            lines.append(
                f"  Job ID      : {j.get('id', 'N/A')}\n"
                f"  Title       : {j.get('Job_Opening_Name', 'N/A')}\n"
                f"  Department  : {j.get('Department', 'N/A')}\n"
                f"  Location    : {j.get('City', 'N/A')}, {j.get('State', 'N/A')}\n"
                f"  Status      : {j.get('Job_Status', status)}\n"
                f"  Posted      : {str(j.get('Date_Opened', 'N/A'))[:10]}\n"
            )
        return "\n".join(lines)
    except RuntimeError as exc:
        return f"Zoho Recruit not configured: {exc}"
    except requests.HTTPError as exc:
        return f"Zoho Recruit API error: {exc.response.status_code} — {exc.response.text[:200]}"
    except Exception as exc:  # noqa: BLE001
        return f"Error fetching Zoho jobs: {exc}"


@tool
def get_zoho_candidates(
    job_id: str = "",
    stage: str = "",
    max_results: int = 50,
) -> str:
    """
    Retrieve candidates from Zoho Recruit, optionally filtered by job or stage.

    Args:
        job_id: Zoho Job Opening ID to filter by (leave empty for all candidates)
        stage: Filter by pipeline stage, e.g. "New", "Screening", "Interview",
               "Offer" (leave empty for all stages)
        max_results: Maximum candidates to return (default 50)

    Returns:
        List of candidates with IDs, names, emails, applied role, and stage.
    """
    try:
        params: dict = {"per_page": max_results}
        if stage:
            params["criteria"] = f"(Candidate_Status:equals:{stage})"

        resp = requests.get(
            f"{ZOHO_BASE}/Candidates/search" if stage else f"{ZOHO_BASE}/Candidates",
            headers=_zoho_headers(),
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("data", [])

        if not candidates:
            return "No candidates found in Zoho Recruit."

        lines = [f"Zoho Recruit Candidates — {len(candidates)} result(s):\n"]
        for c in candidates:
            lines.append(
                f"  Candidate ID : {c.get('id', 'N/A')}\n"
                f"  Name         : {c.get('Full_Name', 'N/A')}\n"
                f"  Email        : {c.get('Email', 'N/A')}\n"
                f"  Phone        : {c.get('Mobile', 'N/A')}\n"
                f"  Stage        : {c.get('Candidate_Status', 'N/A')}\n"
                f"  Experience   : {c.get('Experience_in_Years', 'N/A')} years\n"
                f"  Applied      : {str(c.get('Created_Time', 'N/A'))[:10]}\n"
            )
        return "\n".join(lines)
    except RuntimeError as exc:
        return f"Zoho Recruit not configured: {exc}"
    except requests.HTTPError as exc:
        return f"Zoho Recruit API error: {exc.response.status_code} — {exc.response.text[:200]}"
    except Exception as exc:  # noqa: BLE001
        return f"Error fetching Zoho candidates: {exc}"


@tool
def update_zoho_candidate(
    candidate_id: str,
    stage: str = "",
    notes: str = "",
    score: int = 0,
) -> str:
    """
    Update a candidate's stage in Zoho Recruit and add AI screening notes.
    Use this to push screening results back into Zoho after evaluating a resume.

    Args:
        candidate_id: Zoho Candidate ID (from get_zoho_candidates)
        stage: New pipeline stage — "New", "Screening", "Interview",
               "Offer", "Hired", "Rejected"
        notes: Screening notes to attach (e.g. AI score and summary)
        score: AI screening score 0-100 (stored as a custom field note)

    Returns:
        Confirmation of the update.
    """
    try:
        headers = _zoho_headers()
        results = []

        # Update candidate stage
        if stage:
            update_data = {"data": [{"id": candidate_id, "Candidate_Status": stage}]}
            resp = requests.put(
                f"{ZOHO_BASE}/Candidates",
                headers=headers,
                json=update_data,
                timeout=15,
            )
            if resp.ok:
                results.append(f"Stage updated to '{stage}'.")
            else:
                results.append(f"Stage update failed: {resp.status_code} — {resp.text[:100]}")

        # Add notes
        if notes:
            note_text = notes
            if score:
                note_text = f"AI Screening Score: {score}/100\n\n{notes}"

            note_data = {
                "data": [{
                    "Note_Title": "AI Screening Result",
                    "Note_Content": note_text,
                    "Parent_Id": {"id": candidate_id},
                    "$se_module": "Candidates",
                }]
            }
            note_resp = requests.post(
                f"{ZOHO_BASE}/Notes",
                headers=headers,
                json=note_data,
                timeout=15,
            )
            if note_resp.ok:
                results.append("Screening notes added to candidate record.")
            else:
                results.append(f"Note failed: {note_resp.status_code} — {note_resp.text[:100]}")

        return (
            f"Zoho Recruit candidate {candidate_id} updated.\n"
            + "\n".join(results)
        )
    except RuntimeError as exc:
        return f"Zoho Recruit not configured: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"Error updating Zoho candidate: {exc}"


# ===========================================================================
# WORKABLE TOOLS
# ===========================================================================

@tool
def list_workable_jobs(state: str = "published") -> str:
    """
    List all jobs in Workable.

    Args:
        state: Filter by job state — "published", "draft", "archived", "closed"
               (default: "published")

    Returns:
        List of jobs with shortcodes, titles, departments, and locations.
    """
    try:
        resp = requests.get(
            f"{_workable_base()}/jobs",
            headers=_workable_headers(),
            params={"state": state, "limit": 50},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        jobs = data.get("jobs", [])

        if not jobs:
            return f"No {state} jobs found in Workable."

        lines = [f"Workable Jobs ({state}) — {len(jobs)} total:\n"]
        for j in jobs:
            dept = j.get("department", "N/A")
            location = j.get("location", {})
            loc_str = location.get("city", "") if isinstance(location, dict) else str(location)
            lines.append(
                f"  Shortcode   : {j.get('shortcode', 'N/A')}\n"
                f"  Title       : {j.get('title', 'N/A')}\n"
                f"  Department  : {dept}\n"
                f"  Location    : {loc_str or 'Remote'}\n"
                f"  State       : {j.get('state', state)}\n"
                f"  Created     : {str(j.get('created_at', 'N/A'))[:10]}\n"
            )
        return "\n".join(lines)
    except RuntimeError as exc:
        return f"Workable not configured: {exc}"
    except requests.HTTPError as exc:
        return f"Workable API error: {exc.response.status_code} — {exc.response.text[:200]}"
    except Exception as exc:  # noqa: BLE001
        return f"Error fetching Workable jobs: {exc}"


@tool
def get_workable_candidates(
    job_shortcode: str = "",
    stage: str = "",
    max_results: int = 50,
) -> str:
    """
    Retrieve candidates from Workable, optionally filtered by job or stage.

    Args:
        job_shortcode: Workable job shortcode to filter by (from list_workable_jobs).
                       Leave empty to get candidates across all jobs.
        stage: Filter by pipeline stage name, e.g. "Applied", "Phone Screen",
               "Interview" (leave empty for all stages)
        max_results: Maximum candidates to return (default 50)

    Returns:
        List of candidates with IDs, names, emails, applied job, and stage.
    """
    try:
        params: dict = {"limit": max_results}
        if stage:
            params["stage_slug"] = stage.lower().replace(" ", "-")

        if job_shortcode:
            url = f"{_workable_base()}/jobs/{job_shortcode}/candidates"
        else:
            url = f"{_workable_base()}/candidates"

        resp = requests.get(
            url,
            headers=_workable_headers(),
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])

        if not candidates:
            return "No candidates found in Workable."

        lines = [f"Workable Candidates — {len(candidates)} result(s):\n"]
        for c in candidates:
            job = c.get("job", {})
            job_title = job.get("title", "N/A") if isinstance(job, dict) else "N/A"
            stage_info = c.get("stage", {})
            stage_name = stage_info.get("name", "N/A") if isinstance(stage_info, dict) else "N/A"
            lines.append(
                f"  Candidate ID : {c.get('id', 'N/A')}\n"
                f"  Name         : {c.get('name', 'N/A')}\n"
                f"  Email        : {c.get('email', 'N/A')}\n"
                f"  Job          : {job_title}\n"
                f"  Stage        : {stage_name}\n"
                f"  Applied      : {str(c.get('created_at', 'N/A'))[:10]}\n"
            )
        return "\n".join(lines)
    except RuntimeError as exc:
        return f"Workable not configured: {exc}"
    except requests.HTTPError as exc:
        return f"Workable API error: {exc.response.status_code} — {exc.response.text[:200]}"
    except Exception as exc:  # noqa: BLE001
        return f"Error fetching Workable candidates: {exc}"


@tool
def update_workable_candidate(
    candidate_id: str,
    job_shortcode: str,
    action: str,
    notes: str = "",
    score: int = 0,
) -> str:
    """
    Move a Workable candidate to the next stage, disqualify them, or add comments.
    Use this after AI screening to push results back into Workable.

    Args:
        candidate_id: Workable Candidate ID (from get_workable_candidates)
        job_shortcode: The job shortcode the candidate applied to
        action: "advance" to move to next stage, "disqualify" to reject,
                "comment" to add a note only
        notes: Comment/notes to add (AI screening summary and score)
        score: AI screening score 0-100 (included in the comment)

    Returns:
        Confirmation of the update.
    """
    try:
        headers = _workable_headers()
        base = _workable_base()
        results = []

        # Add comment if notes provided
        if notes:
            comment_text = notes
            if score:
                comment_text = f"AI Screening Score: {score}/100\n\n{notes}"
            comment_resp = requests.post(
                f"{base}/jobs/{job_shortcode}/candidates/{candidate_id}/comments",
                headers=headers,
                json={"comment": {"body": comment_text, "policy": "private"}},
                timeout=15,
            )
            if comment_resp.ok:
                results.append("Screening notes added.")
            else:
                results.append(f"Comment failed: {comment_resp.status_code} — {comment_resp.text[:100]}")

        if action == "advance":
            move_resp = requests.post(
                f"{base}/jobs/{job_shortcode}/candidates/{candidate_id}/move",
                headers=headers,
                json={},
                timeout=15,
            )
            if move_resp.ok:
                results.append("Candidate moved to next stage.")
            else:
                results.append(f"Move failed: {move_resp.status_code} — {move_resp.text[:100]}")

        elif action == "disqualify":
            disq_resp = requests.delete(
                f"{base}/jobs/{job_shortcode}/candidates/{candidate_id}",
                headers=headers,
                timeout=15,
            )
            if disq_resp.ok:
                results.append("Candidate disqualified.")
            else:
                results.append(
                    f"Disqualify failed: {disq_resp.status_code} — {disq_resp.text[:100]}"
                )

        elif action == "comment":
            if not notes:
                results.append("No comment content provided.")

        else:
            return f"Unknown action '{action}'. Use 'advance', 'disqualify', or 'comment'."

        return (
            f"Workable candidate {candidate_id} updated.\n"
            + "\n".join(results)
        )
    except RuntimeError as exc:
        return f"Workable not configured: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"Error updating Workable candidate: {exc}"
