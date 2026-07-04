"""
Agent base — shared LLM and grounding contract.

Single source for the LLM configuration so we don't pin Groq in 8 different
places. When the multi-provider fallback (Groq → Gemini → Anthropic) lands,
it lands here, and every agent inherits it for free.
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


# The same hard rules used by services/ai_client.GROUNDING_CONTRACT, restated
# here as agent backstory text. Any new agent in registry.py should append
# this to its backstory.
GROUNDING_CONTRACT = (
    "You are an analyst that answers STRICTLY from the inputs and tool outputs you receive. "
    "Hard rules: "
    "(1) Use ONLY facts present in the provided inputs and tool outputs. Do NOT use outside "
    "knowledge for numeric claims. "
    "(2) If a requested field cannot be supported by what you've been given, set its value to "
    "null and add an entry to `data_gaps` explaining what was missing. "
    "(3) Every rationale, pro, con, or risk item must be an object {text, source} where "
    "`source` names the input path or tool that backs the claim. No bare strings. "
    "(4) Output a top-level `confidence` field: 'low' | 'medium' | 'high'. 'high' only if "
    "every numeric field is directly present in the inputs/tools. "
    "(5) The user is unregistered with SEBI — describe rather than direct. Phrase outputs as "
    "educational signals, not actionable advice."
)


_llm_singleton = None


def get_llm():
    """Return a CrewAI-compatible LLM. Lazy-imported so missing crewai doesn't break unrelated imports."""
    global _llm_singleton
    if _llm_singleton is not None:
        return _llm_singleton

    openai_key = os.getenv("OPENAI_API_KEY")
    xai_key = os.getenv("XAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if not openai_key and not xai_key and not groq_key:
        raise RuntimeError(
            "None of OPENAI_API_KEY, XAI_API_KEY, or GROQ_API_KEY is set — agent crews are disabled. "
            "Please set one of them in your .env file."
        )

    try:
        from crewai import LLM  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "crewai not installed. pip install crewai crewai-tools (see requirements.txt)."
        ) from e

    if openai_key:
        model = os.getenv("CREWAI_MODEL", "openai/" + os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        api_key = openai_key
    elif xai_key:
        model = os.getenv("CREWAI_MODEL", "xai/" + os.getenv("XAI_MODEL", "grok-3-mini"))
        api_key = xai_key
    else:
        model = os.getenv("CREWAI_MODEL", "groq/" + os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
        api_key = groq_key

    _llm_singleton = LLM(
        model=model,
        api_key=api_key,
        temperature=float(os.getenv("CREWAI_TEMPERATURE", "0.2")),
    )
    logger.info("CrewAI LLM initialized (model=%s).", model)
    return _llm_singleton


def is_available() -> bool:
    """Cheap check the router can use to decide whether to take the agent path."""
    if not os.getenv("GROQ_API_KEY") and not os.getenv("OPENAI_API_KEY") and not os.getenv("XAI_API_KEY"):
        return False
    try:
        import crewai  # noqa: F401
        return True
    except ImportError:
        return False


def _reset_llm():
    """Reset the LLM singleton. Useful for testing/resiliency."""
    global _llm_singleton
    _llm_singleton = None
