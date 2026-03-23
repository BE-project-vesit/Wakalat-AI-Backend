"""Pydantic models for benchmark task files."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class VerifiableFact(BaseModel):
    """Single objective check against parsed tool output (JSON path -> expected)."""

    json_path: str = Field(
        description="Dot path into parsed JSON, e.g. article_reference or matched_category"
    )
    equals: Any | None = None
    contains: str | None = None
    one_of: list[Any] | None = None


class BenchmarkTask(BaseModel):
    """One row in benchmark_tasks.yaml."""

    id: str
    prompt: str = Field(description="Lawyer-facing question (for rubric / end-to-end runs).")
    scope: Literal["tool_only", "end_to_end"] = "tool_only"
    tool: str = Field(description="MCP tool name as in server.py call_tool.")
    tool_args: dict[str, Any] = Field(default_factory=dict)
    verifiable_facts: list[VerifiableFact] = Field(default_factory=list)
    expected_tool: str | None = Field(
        default=None,
        description="For end_to_end runs: ideal tool choice for tool-appropriateness metric.",
    )
    rubric_id: str = Field(
        default="legal_quality_v1",
        description="Key into metrics_spec.yaml human rubrics.",
    )
    difficulty: Literal["easy", "medium", "hard"] = "easy"
    domain_tags: list[str] = Field(default_factory=list)
    requires_network: bool = Field(
        default=False,
        description="If true, skipped when --offline is passed.",
    )
    notes: str | None = None


class BenchmarkSuite(BaseModel):
    version: str = "1"
    tasks: list[BenchmarkTask]
