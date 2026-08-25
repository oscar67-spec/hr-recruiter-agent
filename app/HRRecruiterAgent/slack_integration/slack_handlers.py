"""
Slack event handlers for HR Recruiter Agent.
"""


def register_handlers(app):
    """Register all Slack event handlers."""

    @app.event("app_home_opened")
    def update_home_tab(client, event, logger):
        """Update the App Home tab when a user opens it."""
        try:
            client.views_publish(
                user_id=event["user"],
                view={
                    "type": "home",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Welcome to HR Recruiter Agent!* :wave:"
                            }
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*What I can do:*\n\n"
                                        ":page_facing_up: Generate professional job postings\n"
                                        ":mag: Screen candidate resumes with AI\n"
                                        ":bar_chart: Show ranked candidate dashboards\n"
                                        ":email: Draft interview invitation emails\n"
                                        ":file_folder: List all open positions"
                            }
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*How to use:*\n\n"
                                        "1. Send me a DM with your request\n"
                                        "2. Mention me in a channel: @HRRecruiter\n"
                                        "3. Use slash commands:\n"
                                        "   • `/hr-jobs` - List open positions\n"
                                        "   • `/hr-candidates` - View top candidates\n"
                                        "   • `/hr-screen` - Screen a resume\n"
                                        "   • `/hr-generate` - Generate a job posting"
                            }
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Example requests:*\n\n"
                                        '• "Generate a job posting for Senior DevOps Engineer"\n'
                                        '• "List all open job postings"\n'
                                        '• "Show me candidates with score 80+"\n'
                                        '• "Draft an interview email for Jane Doe"'
                            }
                        }
                    ]
                }
            )
        except Exception as e:
            logger.error(f"Error publishing home tab: {e}")
