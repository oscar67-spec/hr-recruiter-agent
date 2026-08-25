"""
Slack slash commands for HR Recruiter Agent.
"""
from slack_integration.slack_blocks import format_jobs_list, format_candidates_list


def register_commands(app):
    """Register all Slack slash commands."""

    @app.command("/hr-jobs")
    def cmd_list_jobs(ack, respond, command, client):
        """List all open job postings."""
        ack()

        agent = client.agent

        try:
            result = agent("List all open job postings")
            response = result.message

            respond(
                text="Open Job Postings",
                blocks=format_jobs_list(response)
            )
        except Exception as e:
            respond(text=f"Error: {str(e)}")

    @app.command("/hr-candidates")
    def cmd_list_candidates(ack, respond, command, client):
        """List top candidates."""
        ack()

        agent = client.agent
        text = command.get("text", "").strip()

        prompt = "Show me all candidates"
        if text:
            if text.isdigit():
                prompt = f"Show me candidates with score {text} or higher"
            else:
                prompt = f"Show me candidates for {text}"

        try:
            result = agent(prompt)
            response = result.message

            respond(
                text="Top Candidates",
                blocks=format_candidates_list(response)
            )
        except Exception as e:
            respond(text=f"Error: {str(e)}")

    @app.command("/hr-screen")
    def cmd_screen_resume(ack, respond, command):
        """Show instructions for screening a resume."""
        ack()

        respond(
            text="How to screen a resume:",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*How to screen a resume:*\n\n"
                                "1. Send me a DM or mention me in a channel\n"
                                "2. Include the following info:\n"
                                "   • Candidate name and email\n"
                                "   • Job ID or role name\n"
                                "   • Resume text or key highlights\n"
                                "   • Required skills/qualifications\n\n"
                                "*Example:*\n"
                                "```\n"
                                "@HRRecruiter Screen this candidate:\n"
                                "Name: John Smith\n"
                                "Email: john@example.com\n"
                                "Job: Senior Backend Engineer (job_id: abc123)\n"
                                "Resume: 5 years Python, AWS certified, Docker expert...\n"
                                "Requirements: Python, AWS, Docker, REST APIs\n"
                                "```"
                    }
                }
            ]
        )

    @app.command("/hr-generate")
    def cmd_generate_job(ack, respond, command, client):
        """Generate a job posting."""
        ack()

        text = command.get("text", "").strip()

        if not text:
            respond(
                text="Please provide job details. Example:\n"
                     "`/hr-generate Senior DevOps Engineer, Infrastructure, Kubernetes, Terraform, AWS`"
            )
            return

        agent = client.agent

        try:
            result = agent(f"Generate a job posting for {text}")
            response = result.message

            respond(
                text="Generated Job Posting",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": response[:2900]  # Slack block text limit
                        }
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
                                "value": "save_job",
                                "action_id": "save_job_action"
                            }
                        ]
                    }
                ]
            )
        except Exception as e:
            respond(text=f"Error: {str(e)}")

    @app.action("save_job_action")
    def handle_save_job(ack, body, client):
        """Handle save job button click."""
        ack()

        channel_id = body["channel"]["id"]
        client.chat_postMessage(
            channel=channel_id,
            text="To save this job posting, please send me a message with the complete job details and say 'save this job posting'."
        )
