"""
Tests for the legal notice drafting tool.
"""
import json

import pytest

from src.tools import document_drafter


@pytest.mark.asyncio
async def test_draft_notice_rejects_invalid_notice_type():
    result = await document_drafter.draft_notice(
        notice_type="",
        facts="Borrower has not repaid the loan.",
        relief_sought="Repayment within 15 days.",
    )

    payload = json.loads(result)

    assert "error" in payload
    assert "notice_type is required" in payload["error"]


@pytest.mark.asyncio
async def test_draft_notice_returns_error_when_llm_is_not_configured(monkeypatch):
    monkeypatch.setattr(document_drafter, "is_llm_configured", lambda: False)

    result = await document_drafter.draft_notice(
        notice_type="demand",
        facts="Borrower has not repaid Rs. 50,000.",
        relief_sought="Repayment within 15 days.",
    )

    payload = json.loads(result)

    assert payload == {
        "error": (
            "No LLM API key configured. Set GEMINI_API_KEY, OPENAI_API_KEY, or "
            "ANTHROPIC_API_KEY in backend/.env (see .env.example). "
            "Ensure the model id matches your provider (e.g. GEMINI_MODEL=gemini-2.5-flash)."
        )
    }


@pytest.mark.asyncio
async def test_draft_notice_returns_drafted_notice_metadata_and_disclaimer(monkeypatch):
    async def fake_call_llm(prompt: str) -> str:
        assert "NOTICE TYPE: Demand" in prompt
        assert "FACTS OF THE CASE:" in prompt
        assert "RELIEF SOUGHT:" in prompt
        return "Formal legal notice draft"

    monkeypatch.setattr(document_drafter, "is_llm_configured", lambda: True)
    monkeypatch.setattr(document_drafter, "call_llm", fake_call_llm)

    result = await document_drafter.draft_notice(
        notice_type=" demand ",
        facts="Borrower has not repaid Rs. 50,000.",
        relief_sought="Repayment within 15 days.",
        sender_details={"name": "B", "address": "Delhi"},
        recipient_details={"name": "A", "address": "Mumbai"},
    )

    payload = json.loads(result)

    assert payload["notice_type"] == "demand"
    assert payload["drafted_notice"] == "Formal legal notice draft"
    assert payload["metadata"]["requires_review"] is True
    assert payload["metadata"]["sender_details_provided"] is True
    assert payload["metadata"]["recipient_details_provided"] is True
    assert "draft_date" in payload["metadata"]
    assert "AI-generated" in payload["disclaimer"]
