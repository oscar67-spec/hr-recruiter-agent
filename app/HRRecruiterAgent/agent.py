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

SYSTEM_PROMPT = """
You are an intelligent HR and Recruitment Assistant helping department managers
run their end-to-end hiring pipeline.

You can:
1. Generate professional job descriptions (generate_job_posting)
2. Save job postings so teams can refer to them later (save_job_posting)
3. List all open roles and their IDs (list_job_postings)
4. Screen candidate resumes against job requirements (screen_resume)
5. Save screened candidate records (save_candidate)
6. Show a ranked candidate dashboard (list_candidates)
7. Draft interview invitation emails (draft_interview_email)

Guidelines:
- Always confirm before saving anything (job or candidate).
- When screening resumes, extract the score and recommendation from the report
  and offer to save the candidate right away.
- When listing candidates, highlight "Advance" recommendations.
- Keep responses clear and action-oriented for busy hiring managers.
- Ask for missing info rather than making assumptions about role requirements.
- Never use markdown formatting. No asterisks, no bold, no headers, no bullet symbols.
- Write in plain conversational text only. Use plain numbers for lists (1. 2. 3.).
"""


def build_agent() -> Agent:
    model = BedrockModel(
        model_id=BEDROCK_MODEL_ID,
        region_name=AWS_REGION,
        temperature=0.3,
    )
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            generate_job_posting,
            save_job_posting,
            list_job_postings,
            screen_resume,
            save_candidate,
            list_candidates,
            draft_interview_email,
        ],
    )
