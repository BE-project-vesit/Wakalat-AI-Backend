"""
Placeholder for citation_integrity scoring.

Wire Indian Kanoon or find_case_laws to verify that citations mentioned in model text
exist and match metadata. Then call from run_benchmark and set metrics_auto['citation_integrity'].
"""

from __future__ import annotations

from typing import Any


def score_citation_integrity(_parsed_output: dict[str, Any], _task_meta: dict[str, Any]) -> float | None:
    """Return fraction of checked citations verified, or None if no checks configured."""
    return None
