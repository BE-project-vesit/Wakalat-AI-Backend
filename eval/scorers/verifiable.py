"""Evaluate verifiable_facts against parsed tool JSON."""

from __future__ import annotations

from typing import Any

from ..models import VerifiableFact


def get_by_path(data: Any, path: str) -> Any:
    """Return value at dot path for dicts only (missing -> None)."""
    cur: Any = data
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _check_one_fact(parsed: dict[str, Any], fact: VerifiableFact) -> tuple[bool, str]:
    actual = get_by_path(parsed, fact.json_path)
    if fact.equals is not None:
        ok = str(actual) == str(fact.equals) if actual is not None else False
        return ok, f"path={fact.json_path} expected={fact.equals!r} actual={actual!r}"
    if fact.contains is not None:
        text = "" if actual is None else str(actual)
        ok = fact.contains in text
        return ok, f"path={fact.json_path} contains={fact.contains!r} in={text[:200]!r}"
    if fact.one_of is not None:
        ok = actual in fact.one_of
        return ok, f"path={fact.json_path} actual={actual!r} one_of={fact.one_of!r}"
    return False, f"path={fact.json_path} no constraint (equals/contains/one_of) set"


def check_verifiable_facts(
    parsed: dict[str, Any],
    facts: list[VerifiableFact],
) -> tuple[list[dict[str, Any]], bool]:
    """
    Returns (per_fact_results, all_passed).
    If facts is empty, all_passed is True (nothing to fail).
    """
    results: list[dict[str, Any]] = []
    all_passed = True
    for fact in facts:
        passed, detail = _check_one_fact(parsed, fact)
        results.append(
            {
                "json_path": fact.json_path,
                "passed": passed,
                "detail": detail,
            }
        )
        if not passed:
            all_passed = False
    return results, all_passed if facts else True
