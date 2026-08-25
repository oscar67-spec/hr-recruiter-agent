"""
Slack Block Kit formatting helpers for rich message display.
"""


def format_jobs_list(agent_response: str):
    """Format job postings list as Slack blocks."""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Open Job Postings"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```\n{agent_response}\n```"
            }
        }
    ]


def format_candidates_list(agent_response: str):
    """Format candidates dashboard as Slack blocks."""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Candidate Dashboard"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```\n{agent_response}\n```"
            }
        }
    ]


def format_screening_report(candidate_name: str, score: int, report: str):
    """Format resume screening report as Slack blocks with visual indicators."""
    if score >= 80:
        score_emoji = ":star:"
    elif score >= 60:
        score_emoji = ":white_check_mark:"
    else:
        score_emoji = ":x:"

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Screening Report: {candidate_name}"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Score:*\n{score_emoji} {score}/100"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```\n{report}\n```"
            }
        }
    ]


def format_job_posting(role: str, job_description: str):
    """Format generated job posting as Slack blocks."""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Job Posting: {role}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": job_description[:2900]
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Save Job Posting"
                    },
                    "style": "primary",
                    "value": "save_job",
                    "action_id": "save_job_action"
                }
            ]
        }
    ]
