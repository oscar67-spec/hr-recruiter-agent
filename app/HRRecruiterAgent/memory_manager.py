"""
AgentCore Memory integration for the HR Recruiter Agent.

Responsibilities:
  - Lazily discover the deployed memory ID by name (no hardcoded ARN needed).
  - Retrieve semantically relevant memories before each agent turn.
  - Save each conversation turn so the agent learns over time.

All public functions degrade gracefully: if the memory service is unavailable
(e.g. during local dev or before deployment), they return empty strings / no-ops
and log a warning rather than crashing the agent.
"""
from __future__ import annotations

import logging
import threading
from typing import Optional

from config import AWS_REGION, MEMORY_NAME

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy singletons – initialised once per process
# ---------------------------------------------------------------------------

_lock = threading.Lock()
_memory_client = None   # bedrock_agentcore.memory.MemoryClient
_memory_id: Optional[str] = None
_memory_unavailable = False  # set True after first failed discovery to stop retrying


def _get_client():
    """Return (or lazily create) the MemoryClient singleton."""
    global _memory_client
    if _memory_client is None:
        from bedrock_agentcore.memory import MemoryClient  # noqa: PLC0415
        _memory_client = MemoryClient(region_name=AWS_REGION)
    return _memory_client


def get_memory_id() -> Optional[str]:
    """
    Discover the deployed AgentCore Memory ID by name.

    Results are cached per process. Returns None if memory is not yet deployed
    or unavailable — the caller should treat that as "memory disabled".
    """
    global _memory_id, _memory_unavailable

    if _memory_id:
        return _memory_id
    if _memory_unavailable:
        return None

    with _lock:
        # Double-check inside the lock
        if _memory_id or _memory_unavailable:
            return _memory_id

        try:
            client = _get_client()
            memories = client.list_memories()
            for m in memories:
                if m.get("name") == MEMORY_NAME:
                    _memory_id = m.get("memoryId") or m.get("id")
                    logger.info("Memory discovered: id=%s", _memory_id)
                    return _memory_id
            # Memory declared in agentcore.json but not yet deployed
            logger.warning(
                "Memory '%s' not found — deploy with 'agentcore deploy' to enable it.",
                MEMORY_NAME,
            )
        except Exception as exc:
            logger.warning("Memory discovery failed (%s). Continuing without memory.", exc)

        _memory_unavailable = True
        return None


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def retrieve_context(actor_id: str, query: str, top_k: int = 5) -> str:
    """
    Retrieve the most relevant past memories for this actor + query.

    Returns a formatted string ready to be prepended to the agent's context,
    or an empty string if memory is unavailable / returns nothing.
    """
    memory_id = get_memory_id()
    if not memory_id:
        return ""

    try:
        client = _get_client()
        records = client.retrieve_memories(
            memory_id=memory_id,
            actor_id=actor_id,
            query=query,
            top_k=top_k,
        )
        if not records:
            return ""

        lines = ["[Relevant context from your past sessions with this user:]"]
        for record in records:
            # The API may nest content differently across SDK versions — handle both.
            content = record.get("content") or record.get("memoryContent") or record
            if isinstance(content, dict):
                text = (
                    content.get("text")
                    or content.get("value")
                    or str(content)
                )
            else:
                text = str(content)
            text = text.strip()
            if text:
                lines.append(f"- {text}")

        if len(lines) == 1:
            # Only the header — nothing useful retrieved
            return ""

        return "\n".join(lines)

    except Exception as exc:
        logger.warning("Memory retrieval failed (%s). Proceeding without context.", exc)
        return ""


def save_turn(
    actor_id: str,
    session_id: str,
    user_message: str,
    assistant_response: str,
) -> None:
    """
    Persist one conversation turn (user + assistant) to AgentCore Memory.

    Errors are swallowed — a failed save must never crash the agent response.
    Memory is eventually consistent; the content becomes retrievable after the
    service processes the event (typically within a few seconds).
    """
    memory_id = get_memory_id()
    if not memory_id:
        return

    try:
        client = _get_client()
        client.save_conversation(
            memory_id=memory_id,
            actor_id=actor_id,
            session_id=session_id,
            messages=[
                ("user", user_message),
                ("assistant", assistant_response),
            ],
        )
        logger.debug(
            "Turn saved to memory: actor=%s session=%s", actor_id, session_id
        )
    except Exception as exc:
        logger.warning("Memory save failed (%s). Turn not persisted.", exc)
