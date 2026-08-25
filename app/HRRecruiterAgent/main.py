"""
AgentCore Runtime entrypoint for the HR Recruiter Agent.

Uses BedrockAgentCoreApp (Option A SDK) which automatically:
  - Exposes /invocations POST endpoint
  - Exposes /ping GET health-check endpoint
  - Runs on port 8080
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp  # type: ignore[import]

from agent import build_agent

app = BedrockAgentCoreApp()

# Build the Strands agent once at startup (model + tools loaded)
_agent = build_agent()


@app.entrypoint
def invoke(payload: dict) -> dict:
    """
    Handle a single HR agent invocation.

    Expected payload:
        { "prompt": "<user message>" }

    Optional payload fields:
        { "session_id": "<id>" }  – reserved for future session tracking

    Returns:
        { "result": "<agent response text>" }
    """
    user_message = payload.get("prompt", "").strip()
    if not user_message:
        return {
            "result": (
                "No prompt provided. Please send a JSON payload with a "
                "'prompt' key, e.g. {\"prompt\": \"List all open job postings\"}"
            )
        }

    result = _agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
