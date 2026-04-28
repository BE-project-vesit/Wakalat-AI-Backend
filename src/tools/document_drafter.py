"""
Document Drafter Tool
Drafts legal documents like notices, petitions, etc. using LLM
"""
import json
from typing import Optional, Dict, Any
from datetime import datetime
from src.tools.llm import call_llm, is_llm_configured
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

NOTICE_TYPES = frozenset(
    ("demand", "cease_desist", "termination", "breach", "defamation", "other")
)


async def draft_notice(
    notice_type: str,
    facts: str,
    relief_sought: str,
    sender_details: Optional[Dict[str, Any]] = None,
    recipient_details: Optional[Dict[str, Any]] = None
) -> str:
    """
    Draft a legal notice using LLM.

    Args:
        notice_type: Type of legal notice
        facts: Factual background
        relief_sought: Remedy demanded
        sender_details: Details of sender/client
        recipient_details: Details of recipient

    Returns:
        JSON string: success object with drafted_notice, or {"error": "..."}.

    ``notice_type`` must be exactly one of the strings in ``NOTICE_TYPES`` (MCP / clients
    often send \"\" if a dropdown is left blank — that is rejected here with a clear error).
    """
    try:
        raw = notice_type if isinstance(notice_type, str) else ""
        resolved = raw.strip()
        if resolved not in NOTICE_TYPES:
            return json.dumps(
                {
                    "error": (
                        "notice_type is required and must be exactly one of: "
                        "demand, cease_desist, termination, breach, defamation, other. "
                        f"Received: {raw!r}."
                    )
                },
                indent=2,
            )

        logger.info(f"Drafting {resolved} notice")

        if not is_llm_configured():
            return json.dumps(
                {
                    "error": (
                        "No LLM API key configured. Set GEMINI_API_KEY, OPENAI_API_KEY, or "
                        "ANTHROPIC_API_KEY in backend/.env (see .env.example). "
                        "Ensure the model id matches your provider (e.g. GEMINI_MODEL=gemini-2.5-flash)."
                    )
                },
                indent=2,
            )

        current_date = datetime.now().strftime("%B %d, %Y")

        sender_info = "Not provided"
        if sender_details:
            sender_info = "\n".join(f"  {k}: {v}" for k, v in sender_details.items())

        recipient_info = "Not provided"
        if recipient_details:
            recipient_info = "\n".join(f"  {k}: {v}" for k, v in recipient_details.items())

        notice_type_guidance = {
            "demand": "Include specific demand amount, payment deadline, and consequences of non-compliance. Reference relevant provisions of the Indian Contract Act.",
            "cease_desist": "Clearly identify the infringing activity, demand immediate cessation, and cite relevant IP laws or other applicable statutes.",
            "termination": "Reference the agreement being terminated, cite the termination clause, specify the effective date, and outline post-termination obligations.",
            "breach": "Identify the specific breach, reference the breached clauses, quantify damages if applicable, and provide a cure period.",
            "defamation": "Identify the defamatory statements, specify where/when published, demand retraction and apology, and cite Sections 499-500 IPC.",
            "other": "Draft a formal legal notice appropriate to the facts provided, citing relevant Indian legal provisions.",
        }

        prompt = (
            f"You are a senior Indian advocate drafting a formal legal notice. Draft a complete, ready-to-send legal notice.\n\n"
            f"NOTICE TYPE: {resolved.replace('_', ' ').title()}\n"
            f"DATE: {current_date}\n\n"
            f"SENDER DETAILS:\n{sender_info}\n\n"
            f"RECIPIENT DETAILS:\n{recipient_info}\n\n"
            f"FACTS OF THE CASE:\n{facts}\n\n"
            f"RELIEF SOUGHT:\n{relief_sought}\n\n"
            f"GUIDANCE: {notice_type_guidance[resolved]}\n\n"
            f"REQUIREMENTS:\n"
            f"- Use formal Indian legal notice format\n"
            f"- Include 'WITHOUT PREJUDICE' header where appropriate\n"
            f"- Reference specific sections of applicable Indian Acts\n"
            f"- Use actual sender/recipient details provided (use placeholders like [SENDER NAME] only if details not provided)\n"
            f"- Include a compliance deadline (typically 15 days)\n"
            f"- End with consequences of non-compliance\n"
            f"- Include space for advocate signature with enrollment number\n"
            f"- Follow Indian Bar Council professional conduct standards\n\n"
            f"Draft the complete legal notice:"
        )

        notice_text = await call_llm(prompt)

        stripped = (notice_text or "").strip()
        if stripped.startswith("[No LLM API key configured"):
            return json.dumps(
                {
                    "error": (
                        "No LLM API key configured. Set GEMINI_API_KEY, OPENAI_API_KEY, or "
                        "ANTHROPIC_API_KEY in backend/.env (see .env.example)."
                    )
                },
                indent=2,
            )
        if not stripped:
            return json.dumps(
                {"error": "LLM returned empty content. Check API key, model id, and quotas."},
                indent=2,
            )

        result = {
            "notice_type": resolved,
            "drafted_notice": notice_text,
            "metadata": {
                "draft_date": current_date,
                "requires_review": True,
                "sender_details_provided": sender_details is not None,
                "recipient_details_provided": recipient_details is not None,
            },
            "disclaimer": "This draft is AI-generated. Review by qualified legal counsel is mandatory before sending.",
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        # Use {} style — exception text may contain "{" which breaks loguru f-strings
        logger.error("Error drafting notice: {}", str(e), exc_info=True)
        return json.dumps({"error": str(e)}, indent=2)


