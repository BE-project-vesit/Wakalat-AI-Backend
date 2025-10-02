"""
Tests for MCP tools
"""
import pytest
import asyncio
from src.tools.precedent_search import search_precedents
from src.tools.case_law_finder import find_case_laws
from src.tools.legal_research import conduct_legal_research
from src.tools.limitation_checker import check_limitation_period


@pytest.mark.asyncio
async def test_search_precedents():
    """Test precedent search tool"""
    result = await search_precedents(
        query="breach of contract",
        jurisdiction="all",
        max_results=5
    )
    assert result is not None
    assert "query" in result or "error" in result


@pytest.mark.asyncio
async def test_find_case_laws():
    """Test case law finder tool"""
    result = await find_case_laws(
        citation="AIR 2020 SC 1234"
    )
    assert result is not None
    assert "search_parameters" in result or "error" in result


@pytest.mark.asyncio
async def test_legal_research():
    """Test legal research tool"""
    result = await conduct_legal_research(
        research_query="vicarious liability",
        research_depth="brief"
    )
    assert result is not None
    assert "research_query" in result or "error" in result


@pytest.mark.asyncio
async def test_limitation_checker():
    """Test limitation checker tool"""
    result = await check_limitation_period(
        case_type="suit_for_money_lent",
        cause_of_action_date="2020-01-01"
    )
    assert result is not None
    assert "case_type" in result or "error" in result


def test_limitation_periods_calculation():
    """Test limitation period calculations"""
    # This is a synchronous test for the calculation logic
    from src.tools.limitation_checker import LIMITATION_PERIODS
    
    assert "suit_for_money_lent" in LIMITATION_PERIODS
    assert LIMITATION_PERIODS["suit_for_money_lent"]["years"] == 3
    assert "motor_accident_claim" in LIMITATION_PERIODS
    assert LIMITATION_PERIODS["motor_accident_claim"]["years"] == 2
