"""
AgentCore Runtime entrypoint for the HR Recruiter Agent.

Uses BedrockAgentCoreApp (Option A SDK) which automatically:
  - Exposes /invocations POST endpoint
  - Exposes /ping GET health-check endpoint
  - Runs on port 8080

Session handling
----------------
Each unique session_id gets its own Strands Agent instance so that within-session
conversation context is preserved ("yes, save it" works correctly).

Memory
------
Before every turn:
  - Past relevant memories are retrieved from AgentCore Memory and injected
    as context so the agent remembers candidates, roles, and preferences
    from previous sessions.

After every turn:
  - The conversation turn is saved to AgentCore Memory so the agent learns
    over time.

Expected payload fields
-----------------------
  prompt     (str, required)  – The user's message.
  actor_id   (str, optional)  – Stable user identifier (default: "default-user").
                                Use the hiring manager's email / Slack user ID.
  session_id (str, optional)  – Conversation thread ID (default: "default-session").
                                Pass the same ID across turns to maintain context.
"""
import threading
import logging

from bedrock_agentcore.runtime import BedrockAgentCoreApp  # type: ignore[import]

from strands import Agent  # type: ignore[import]

from agent import build_agent
from memory_manager import retrieve_context, save_turn

logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()

# ---------------------------------------------------------------------------
# Per-session agent registry
# ---------------------------------------------------------------------------
# Each session gets its own Strands Agent so conversation history is isolated.
# A single shared agent would bleed context between different users / threads.

_session_agents: dict[str, Agent] = {}
_session_lock = threading.Lock()


def _get_session_agent(session_id: str):
    """Return (or lazily create) the Strands Agent for a given session."""
    with _session_lock:
        if session_id not in _session_agents:
            logger.info("Creating new agent for session: %s", session_id)
            _session_agents[session_id] = build_agent()
        return _session_agents[session_id]


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

@app.entrypoint
def invoke(payload: dict) -> dict:
    """
    Handle a single HR agent invocation.

    Expected payload:
        {
            "prompt":     "<user message>",        # required
            "actor_id":   "<user identifier>",     # optional
            "session_id": "<conversation thread>"  # optional
        }

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

    actor_id   = str(payload.get("actor_id",   "default-user")).strip() or "default-user"
    session_id = str(payload.get("session_id", "default-session")).strip() or "default-session"

    # -- 1. Retrieve relevant past memories -----------------------------------
    memory_context = retrieve_context(actor_id=actor_id, query=user_message)

    # Inject memory context ahead of the user's message so the agent has
    # full recall without the user needing to repeat past context.
    if memory_context:
        augmented_message = f"{memory_context}\n\n{user_message}"
    else:
        augmented_message = user_message

    # -- 2. Run the agent (session-scoped, stateful within session) -----------
    agent = _get_session_agent(session_id)
    result = agent(augmented_message)
    response_text = str(result.message)

    # -- 3. Persist this turn to memory ---------------------------------------
    # Fire-and-forget: errors are swallowed inside save_turn.
    save_turn(
        actor_id=actor_id,
        session_id=session_id,
        user_message=user_message,
        assistant_response=response_text,
    )

    return {"result": response_text}


if __name__ == "__main__":
    app.run()
