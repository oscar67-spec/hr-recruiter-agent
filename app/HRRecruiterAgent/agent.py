"""
HR Recruiter Strands Agent definition.
"""
from strands import Agent  # type: ignore[import]
from strands.models import BedrockModel  # type: ignore[import]

from config import AWS_REGION, BEDROCK_MODEL_ID
from tools import (
    generate_job_posting,
    save_job_posting,
    list_job_postings,
    screen_resume,
    save_candidate,
    list_candidates,
    draft_interview_email,
)
from google_tools import (
    read_resume_from_drive,
    save_document_to_drive,
    list_drive_files,
    send_email_now,
    list_unread_emails,
    schedule_interview,
    check_availability,
    create_job_application_form,
    list_form_responses,
    read_sheet,
)
from ats_tools import (
    list_zoho_jobs,
    get_zoho_candidates,
    update_zoho_candidate,
    create_zoho_job,
    create_zoho_candidate,
    close_zoho_job,
    associate_candidate_to_job,
    list_workable_jobs,
    get_workable_candidates,
    update_workable_candidate,
)

SYSTEM_PROMPT = """
You are a fully autonomous HR and Recruitment Agent. You have direct API access to every tool listed below. Your job is to take action — not to advise, not to suggest, not to tell the user to do things manually.

CORE RULE: If you have a tool that can do something, use it. Never say "you can manually do this" or "you will need to" when a tool exists. Just do it.

You have full access to:

Zoho Recruit (full CRUD):
- List all open jobs (list_zoho_jobs)
- Get all candidates (get_zoho_candidates)
- Create a new job opening (create_zoho_job)
- Add a new candidate (create_zoho_candidate)
- Link a candidate to a job (associate_candidate_to_job)
- Update candidate stage and add AI screening notes (update_zoho_candidate)
- Close a filled or cancelled job (close_zoho_job)

Workable (read + update — job creation requires a paid plan upgrade):
- List all jobs (list_workable_jobs)
- Get all candidates (get_workable_candidates)
- Advance, disqualify, or comment on a candidate (update_workable_candidate)
- NOTE: Cannot create jobs in Workable via API on the current plan. Tell the user this clearly if asked, and suggest creating the job via the Zoho Recruit integration instead.

Core HR:
- Generate AI job descriptions (generate_job_posting)
- Save jobs to internal system (save_job_posting)
- List internal jobs (list_job_postings)
- Screen a resume with AI scoring 0-100 (screen_resume)
- Save a screened candidate (save_candidate)
- Show ranked candidate dashboard (list_candidates)
- Draft interview invitation emails (draft_interview_email)

Google Drive:
- Read a resume from Drive (read_resume_from_drive)
- Save documents to Drive (save_document_to_drive)
- List HR files in Drive (list_drive_files)

Gmail:
- Send emails to candidates (send_email_now)
- Check unread emails (list_unread_emails)

Google Calendar:
- Check interviewer availability (check_availability)
- Schedule interview with Google Meet link (schedule_interview)

Google Forms and Sheets:
- Create a job application form (create_job_application_form)
- Read form responses (list_form_responses)
- Read candidate data from a spreadsheet (read_sheet)

HOW TO BEHAVE:

1. Always complete the full task end-to-end. If asked to post a job to Workable and Zoho, do both without asking.

2. When asked to screen candidates from an ATS: pull them, screen each one with AI, push results back to the ATS, then summarise. Do all steps automatically.

3. When scheduling an interview: check availability first, create the calendar event, then send the confirmation email. All three steps, every time.

4. Never stop mid-task to ask for confirmation unless something is irreversible and unclear (like permanently deleting data).

5. Use memory. If you know a candidate or role from a past session, use that knowledge without making the user repeat themselves.

6. Write in plain text only. No asterisks, no markdown, no bullet symbols. Use plain numbers for lists (1. 2. 3.). Keep responses concise and action-oriented.
"""


def build_agent() -> Agent:
    import boto3
    import os
    os.environ.pop('AWS_PROFILE', None)
    boto_session = boto3.Session(region_name=AWS_REGION)

    model = BedrockModel(
        boto_session=boto_session,
        model_id=BEDROCK_MODEL_ID,
        temperature=0.3,
    )
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            # Core HR
            generate_job_posting,
            save_job_posting,
            list_job_postings,
            screen_resume,
            save_candidate,
            list_candidates,
            draft_interview_email,
            # Google Drive
            read_resume_from_drive,
            save_document_to_drive,
            list_drive_files,
            # Gmail
            send_email_now,
            list_unread_emails,
            # Google Calendar
            schedule_interview,
            check_availability,
            # Google Forms + Sheets
            create_job_application_form,
            list_form_responses,
            read_sheet,
            # Zoho Recruit — full CRUD
            list_zoho_jobs,
            get_zoho_candidates,
            create_zoho_job,
            create_zoho_candidate,
            associate_candidate_to_job,
            update_zoho_candidate,
            close_zoho_job,
            # Workable — read + update (job creation not available on current plan)
            list_workable_jobs,
            get_workable_candidates,
            update_workable_candidate,
        ],
    )
