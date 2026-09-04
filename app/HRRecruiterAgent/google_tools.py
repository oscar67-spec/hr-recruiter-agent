"""
Google integrations for the HR Recruiter Agent.

Provides four groups of @tool functions:

  Google Forms + Sheets
  ---------------------
  - list_form_responses     : Read job application submissions from a Google Form
  - read_sheet              : Read candidate data from a Google Sheet

  Google Drive
  ------------
  - read_resume_from_drive   : Read a resume/document from Drive by name or ID
  - save_document_to_drive   : Save a JD or offer letter to Drive
  - list_drive_files         : List HR files in a Drive folder

  Gmail
  -----
  - send_email_now           : Actually send an email to a candidate or recruiter
  - list_unread_emails       : Check inbox for incoming resumes or replies

  Google Calendar
  ---------------
  - schedule_interview       : Create a calendar event with Meet link and invite attendees
  - check_availability       : Check an interviewer's free/busy slots on a given day

Setup required (one time):
  Run `python setup/google_auth.py` to complete the OAuth flow and store the
  refresh token.  Then add GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and
  GOOGLE_REFRESH_TOKEN to app/HRRecruiterAgent/.env
"""
from __future__ import annotations

import base64
import io
import json
import os
import textwrap
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from strands import tool  # type: ignore[import]

# ---------------------------------------------------------------------------
# Lazy imports — only pulled in when a tool is actually called so that the
# agent still starts (without crashing) even when Google deps are not yet
# installed.
# ---------------------------------------------------------------------------
def _google_creds():
    """Return a valid, refreshed Google OAuth2 Credentials object."""
    try:
        from google.auth.transport.requests import Request  # type: ignore[import]
        from google.oauth2.credentials import Credentials  # type: ignore[import]
    except ImportError:
        raise RuntimeError(
            "Google client libraries not installed.  "
            "Run: uv add google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )

    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN", "")

    if not all([client_id, client_secret, refresh_token]):
        raise RuntimeError(
            "Google credentials not configured.  "
            "Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REFRESH_TOKEN in .env.  "
            "Run setup/google_auth.py to obtain the refresh token."
        )

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=[
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/forms.responses.readonly",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        ],
    )
    creds.refresh(Request())
    return creds


def _drive():
    from googleapiclient.discovery import build  # type: ignore[import]
    return build("drive", "v3", credentials=_google_creds())


def _gmail():
    from googleapiclient.discovery import build  # type: ignore[import]
    return build("gmail", "v1", credentials=_google_creds())


def _calendar():
    from googleapiclient.discovery import build  # type: ignore[import]
    return build("calendar", "v3", credentials=_google_creds())


def _extract_text_from_drive_file(service, file_id: str, mime_type: str) -> str:
    """Download a Drive file and return its text content."""
    from googleapiclient.http import MediaIoBaseDownload  # type: ignore[import]

    # Google Docs → export as plain text
    if mime_type == "application/vnd.google-apps.document":
        data = (
            service.files()
            .export(fileId=file_id, mimeType="text/plain")
            .execute()
        )
        return data.decode("utf-8") if isinstance(data, bytes) else str(data)

    # PDF → download then extract text
    if mime_type == "application/pdf":
        buf = io.BytesIO()
        request = service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        buf.seek(0)
        try:
            from pypdf import PdfReader  # type: ignore[import]
            reader = PdfReader(buf)
            return "\n".join(
                page.extract_text() or "" for page in reader.pages
            )
        except ImportError:
            return (
                "[PDF text extraction requires pypdf.  "
                "Run: uv add pypdf]"
            )

    # Plain text / other
    buf = io.BytesIO()
    request = service.files().get_media(fileId=file_id)
    from googleapiclient.http import MediaIoBaseDownload  # type: ignore[import]
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue().decode("utf-8", errors="replace")


# ===========================================================================
# GOOGLE DRIVE TOOLS
# ===========================================================================

@tool
def read_resume_from_drive(file_name: str) -> str:
    """
    Read a resume or document from Google Drive by file name (or partial name).
    Returns the full text content so the agent can screen it.

    Args:
        file_name: Name or partial name of the file in Google Drive
                   (e.g. "John_Smith_Resume" or "john resume")

    Returns:
        Full text content of the file, ready for resume screening.
    """
    try:
        svc = _drive()
        # Search by name (partial match, not trashed)
        query = f"name contains '{file_name}' and trashed = false"
        result = (
            svc.files()
            .list(
                q=query,
                fields="files(id, name, mimeType)",
                pageSize=5,
                orderBy="modifiedTime desc",
            )
            .execute()
        )
        files = result.get("files", [])
        if not files:
            return (
                f"No file found in Google Drive matching '{file_name}'.  "
                "Check the file name and make sure it is not in the Trash."
            )
        # Pick the first (most recently modified) match
        file = files[0]
        text = _extract_text_from_drive_file(svc, file["id"], file["mimeType"])
        header = f"File: {file['name']} (Drive ID: {file['id']})\n{'=' * 60}\n"
        return header + text[:8000]  # cap at 8 k chars
    except RuntimeError as exc:
        return f"Google Drive not configured: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"Error reading from Google Drive: {exc}"


@tool
def save_document_to_drive(
    filename: str,
    content: str,
    folder_name: str = "HR Recruiter",
) -> str:
    """
    Save a document (job description, offer letter, notes) to Google Drive.
    Creates the HR Recruiter folder if it does not exist.

    Args:
        filename: Name to give the file (e.g. "Senior_Engineer_JD.txt")
        content: Full text content to save
        folder_name: Drive folder to save into (default: "HR Recruiter")

    Returns:
        Confirmation with a link to the created file.
    """
    try:
        from googleapiclient.http import MediaInMemoryUpload  # type: ignore[import]

        svc = _drive()

        # Find or create the folder
        folder_q = (
            f"name = '{folder_name}' "
            "and mimeType = 'application/vnd.google-apps.folder' "
            "and trashed = false"
        )
        folder_result = (
            svc.files().list(q=folder_q, fields="files(id, name)").execute()
        )
        folder_files = folder_result.get("files", [])
        if folder_files:
            folder_id = folder_files[0]["id"]
        else:
            folder_meta = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            created = svc.files().create(body=folder_meta, fields="id").execute()
            folder_id = created["id"]

        # Upload the file
        media = MediaInMemoryUpload(
            content.encode("utf-8"), mimetype="text/plain", resumable=False
        )
        file_meta = {"name": filename, "parents": [folder_id]}
        uploaded = (
            svc.files()
            .create(body=file_meta, media_body=media, fields="id, webViewLink")
            .execute()
        )
        link = uploaded.get("webViewLink", "")
        return (
            f"Document saved to Google Drive.\n"
            f"Folder  : {folder_name}\n"
            f"File    : {filename}\n"
            f"Link    : {link}"
        )
    except RuntimeError as exc:
        return f"Google Drive not configured: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"Error saving to Google Drive: {exc}"


@tool
def list_drive_files(
    folder_name: str = "HR Recruiter",
    query: str = "",
) -> str:
    """
    List files in a Google Drive folder, optionally filtered by a search term.

    Args:
        folder_name: Folder to list (default: "HR Recruiter")
        query: Optional keyword to filter file names (e.g. "resume", "JD")

    Returns:
        List of files with names, types, and last-modified dates.
    """
    try:
        svc = _drive()

        # Find folder
        folder_q = (
            f"name = '{folder_name}' "
            "and mimeType = 'application/vnd.google-apps.folder' "
            "and trashed = false"
        )
        folder_result = (
            svc.files().list(q=folder_q, fields="files(id, name)").execute()
        )
        folders = folder_result.get("files", [])
        if not folders:
            return f"Folder '{folder_name}' not found in Google Drive."
        folder_id = folders[0]["id"]

        # List files in folder
        name_filter = f" and name contains '{query}'" if query else ""
        files_q = f"'{folder_id}' in parents and trashed = false{name_filter}"
        result = (
            svc.files()
            .list(
                q=files_q,
                fields="files(id, name, mimeType, modifiedTime)",
                orderBy="modifiedTime desc",
                pageSize=50,
            )
            .execute()
        )
        files = result.get("files", [])
        if not files:
            return f"No files found in '{folder_name}'{' matching ' + query if query else ''}."

        lines = [f"Files in Google Drive / {folder_name} ({len(files)} total):\n"]
        for i, f in enumerate(files, 1):
            modified = f.get("modifiedTime", "")[:10]
            mime = f.get("mimeType", "").split(".")[-1]
            lines.append(f"  {i}. {f['name']}  [{mime}]  modified {modified}")
        return "\n".join(lines)
    except RuntimeError as exc:
        return f"Google Drive not configured: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"Error listing Google Drive files: {exc}"


# ===========================================================================
# GMAIL TOOLS
# ===========================================================================

@tool
def send_email_now(
    to_email: str,
    to_name: str,
    subject: str,
    body: str,
) -> str:
    """
    Send an email immediately via Gmail (interview invites, offer letters,
    rejection notices, follow-ups).

    Args:
        to_email: Recipient email address
        to_name: Recipient full name
        subject: Email subject line
        body: Full email body text (plain text)

    Returns:
        Confirmation that the email was sent, with Gmail message ID.
    """
    try:
        svc = _gmail()
        msg = MIMEMultipart("alternative")
        msg["To"] = f"{to_name} <{to_email}>"
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        sent = (
            svc.users()
            .messages()
            .send(userId="me", body={"raw": raw})
            .execute()
        )
        return (
            f"Email sent successfully.\n"
            f"To      : {to_name} <{to_email}>\n"
            f"Subject : {subject}\n"
            f"Gmail ID: {sent.get('id', 'N/A')}"
        )
    except RuntimeError as exc:
        return f"Gmail not configured: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"Error sending email: {exc}"


@tool
def list_unread_emails(
    search_query: str = "is:unread",
    max_results: int = 10,
) -> str:
    """
    List recent emails from Gmail, useful for checking incoming resumes,
    candidate replies, or interview confirmations.

    Args:
        search_query: Gmail search query (default: unread emails).
                      Examples: "is:unread resume", "from:candidate@email.com",
                      "subject:application"
        max_results: Maximum number of emails to return (default 10)

    Returns:
        List of email summaries with sender, subject, and date.
    """
    try:
        svc = _gmail()
        results = (
            svc.users()
            .messages()
            .list(userId="me", q=search_query, maxResults=max_results)
            .execute()
        )
        messages = results.get("messages", [])
        if not messages:
            return f"No emails found matching: {search_query}"

        lines = [f"Found {len(messages)} email(s) matching '{search_query}':\n"]
        for i, msg_ref in enumerate(messages, 1):
            msg = (
                svc.users()
                .messages()
                .get(userId="me", id=msg_ref["id"], format="metadata",
                     metadataHeaders=["From", "Subject", "Date"])
                .execute()
            )
            headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
            snippet = msg.get("snippet", "")[:100]
            lines.append(
                f"  {i}. From   : {headers.get('From', 'Unknown')}\n"
                f"     Subject: {headers.get('Subject', '(no subject)')}\n"
                f"     Date   : {headers.get('Date', 'Unknown')}\n"
                f"     Preview: {snippet}...\n"
            )
        return "\n".join(lines)
    except RuntimeError as exc:
        return f"Gmail not configured: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"Error reading Gmail: {exc}"


# ===========================================================================
# GOOGLE CALENDAR TOOLS
# ===========================================================================

@tool
def schedule_interview(
    candidate_name: str,
    candidate_email: str,
    interviewer_email: str,
    role: str,
    date_time_iso: str,
    duration_minutes: int = 45,
    notes: str = "",
) -> str:
    """
    Create a Google Calendar interview event with a Google Meet link.
    Sends calendar invitations to both the candidate and the interviewer.

    Args:
        candidate_name: Full name of the candidate
        candidate_email: Candidate's email address
        interviewer_email: Interviewer's Google account email
        role: Role being interviewed for (used in event title)
        date_time_iso: Interview start time in ISO 8601 format
                       (e.g. "2026-09-10T14:00:00" for 2pm on Sep 10)
        duration_minutes: Interview length in minutes (default 45)
        notes: Optional agenda or preparation notes to include in the event

    Returns:
        Confirmation with calendar event link and Google Meet link.
    """
    try:
        svc = _calendar()

        start_dt = datetime.fromisoformat(date_time_iso)
        # Assume local timezone if no tz info
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        end_dt = start_dt + timedelta(minutes=duration_minutes)

        description_parts = [
            f"Interview for the {role} position.",
            f"Candidate: {candidate_name} ({candidate_email})",
        ]
        if notes:
            description_parts.append(f"\nAgenda / Notes:\n{notes}")

        event = {
            "summary": f"Interview: {candidate_name} — {role}",
            "description": "\n".join(description_parts),
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "UTC",
            },
            "attendees": [
                {"email": candidate_email, "displayName": candidate_name},
                {"email": interviewer_email},
            ],
            "conferenceData": {
                "createRequest": {
                    "requestId": f"hr-interview-{candidate_email}-{role}".replace(" ", "-").lower(),
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 1440},   # 1 day before
                    {"method": "popup", "minutes": 30},
                ],
            },
        }

        created = (
            svc.events()
            .insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1,
                sendUpdates="all",
            )
            .execute()
        )

        meet_link = ""
        conf = created.get("conferenceData", {})
        for ep in conf.get("entryPoints", []):
            if ep.get("entryPointType") == "video":
                meet_link = ep.get("uri", "")
                break

        return (
            f"Interview scheduled.\n"
            f"Event   : {created.get('summary')}\n"
            f"When    : {start_dt.strftime('%A %B %d, %Y at %I:%M %p UTC')} "
            f"({duration_minutes} minutes)\n"
            f"Meet    : {meet_link or 'link being generated'}\n"
            f"Calendar: {created.get('htmlLink', '')}\n"
            f"Invites sent to {candidate_email} and {interviewer_email}."
        )
    except RuntimeError as exc:
        return f"Google Calendar not configured: {exc}"
    except ValueError as exc:
        return (
            f"Invalid date format: {exc}.  "
            "Use ISO 8601 format, e.g. '2026-09-10T14:00:00'"
        )
    except Exception as exc:  # noqa: BLE001
        return f"Error scheduling interview: {exc}"


@tool
def check_availability(
    interviewer_email: str,
    date: str,
) -> str:
    """
    Check an interviewer's Google Calendar availability on a given day
    to find open slots for scheduling interviews.

    Args:
        interviewer_email: Interviewer's Google account email
        date: Date to check in YYYY-MM-DD format (e.g. "2026-09-10")

    Returns:
        List of busy time blocks and suggested free windows during business hours.
    """
    try:
        svc = _calendar()

        day_start = datetime.fromisoformat(f"{date}T00:00:00+00:00")
        day_end = datetime.fromisoformat(f"{date}T23:59:59+00:00")

        body = {
            "timeMin": day_start.isoformat(),
            "timeMax": day_end.isoformat(),
            "items": [{"id": interviewer_email}],
        }
        result = svc.freebusy().query(body=body).execute()
        busy_slots = result.get("calendars", {}).get(interviewer_email, {}).get("busy", [])

        if not busy_slots:
            return (
                f"{interviewer_email} appears fully free on {date}.  "
                "Any slot between 9am-5pm UTC should work."
            )

        lines = [f"Busy times for {interviewer_email} on {date}:\n"]
        for slot in busy_slots:
            start = slot["start"][11:16]
            end = slot["end"][11:16]
            lines.append(f"  - {start} to {end} UTC (busy)")

        # Suggest gaps in 9am-5pm window
        business_hours = [(9, 0), (17, 0)]
        busy_parsed = [
            (
                int(s["start"][11:13]) * 60 + int(s["start"][14:16]),
                int(s["end"][11:13]) * 60 + int(s["end"][14:16]),
            )
            for s in busy_slots
        ]
        busy_parsed.sort()

        free_windows = []
        current = business_hours[0][0] * 60
        end_of_day = business_hours[1][0] * 60
        for b_start, b_end in busy_parsed:
            if current < b_start:
                free_windows.append((current, b_start))
            current = max(current, b_end)
        if current < end_of_day:
            free_windows.append((current, end_of_day))

        if free_windows:
            lines.append("\nSuggested free windows (UTC):")
            for ws, we in free_windows:
                if we - ws >= 45:  # only show slots long enough for an interview
                    lines.append(
                        f"  - {ws // 60:02d}:{ws % 60:02d} to {we // 60:02d}:{we % 60:02d}"
                    )

        return "\n".join(lines)
    except RuntimeError as exc:
        return f"Google Calendar not configured: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"Error checking availability: {exc}"


def _forms():
    from googleapiclient.discovery import build  # type: ignore[import]
    return build("forms", "v1", credentials=_google_creds())


def _sheets():
    from googleapiclient.discovery import build  # type: ignore[import]
    return build("sheets", "v4", credentials=_google_creds())


# ===========================================================================
# GOOGLE FORMS TOOLS
# ===========================================================================

@tool
def list_form_responses(
    form_id: str,
    max_responses: int = 50,
) -> str:
    """
    Read job application submissions from a Google Form.
    Use this when candidates apply via a Google Form — the agent reads
    all responses and can screen each applicant automatically.

    Args:
        form_id: The Google Form ID (found in the form URL:
                 docs.google.com/forms/d/{FORM_ID}/edit)
        max_responses: Maximum number of responses to return (default 50)

    Returns:
        List of form responses with each question and answer per applicant.
    """
    try:
        svc = _forms()

        # Get form metadata (question titles)
        form = svc.forms().get(formId=form_id).execute()
        questions = {}
        for item in form.get("items", []):
            q_id = item.get("questionItem", {}).get("question", {}).get("questionId", "")
            title = item.get("title", "")
            if q_id:
                questions[q_id] = title

        # Get responses
        responses_result = (
            svc.forms()
            .responses()
            .list(formId=form_id)
            .execute()
        )
        responses = responses_result.get("responses", [])[:max_responses]

        if not responses:
            return f"No responses found for form {form_id}."

        form_title = form.get("info", {}).get("title", "Google Form")
        lines = [f"Form: {form_title}\nResponses: {len(responses)}\n{'=' * 60}\n"]

        for i, resp in enumerate(responses, 1):
            lines.append(f"Applicant {i} — submitted {resp.get('lastSubmittedTime', 'N/A')[:10]}")
            answers = resp.get("answers", {})
            for q_id, answer_data in answers.items():
                question = questions.get(q_id, q_id)
                text_answers = answer_data.get("textAnswers", {}).get("answers", [])
                answer = ", ".join(a.get("value", "") for a in text_answers)
                lines.append(f"  {question}: {answer}")
            lines.append("")

        return "\n".join(lines)
    except RuntimeError as exc:
        return f"Google Forms not configured: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"Error reading Google Form responses: {exc}"


# ===========================================================================
# GOOGLE SHEETS TOOLS
# ===========================================================================

@tool
def read_sheet(
    spreadsheet_id: str,
    sheet_name: str = "Sheet1",
    max_rows: int = 100,
) -> str:
    """
    Read candidate or job data from a Google Sheet.
    Useful when recruiters track applicants or job postings in a spreadsheet.

    Args:
        spreadsheet_id: The Google Sheets ID (found in the URL:
                        docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit)
        sheet_name: Name of the sheet tab to read (default: "Sheet1")
        max_rows: Maximum number of rows to return (default 100)

    Returns:
        Formatted table of sheet data with headers and rows.
    """
    try:
        svc = _sheets()
        range_name = f"{sheet_name}!A1:Z{max_rows}"
        result = (
            svc.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        rows = result.get("values", [])
        if not rows:
            return f"No data found in sheet '{sheet_name}'."

        headers = rows[0] if rows else []
        data_rows = rows[1:]

        lines = [f"Google Sheet — {len(data_rows)} row(s) of data:\n"]
        lines.append(" | ".join(headers))
        lines.append("-" * 80)
        for row in data_rows:
            # Pad row to match header length
            padded = row + [""] * (len(headers) - len(row))
            lines.append(" | ".join(str(v) for v in padded[:len(headers)]))

        return "\n".join(lines)
    except RuntimeError as exc:
        return f"Google Sheets not configured: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"Error reading Google Sheet: {exc}"
