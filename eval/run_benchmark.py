"""
Run Wakalat MCP tool benchmark: execute golden tasks, score verifiable facts, write artifacts.

Usage (from Wakalat-AI-Backend/):
  python -m eval.run_benchmark
  python -m eval.run_benchmark --offline
  python -m eval.run_benchmark --task lim_money_lent_article
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .models import BenchmarkSuite, BenchmarkTask
from .scorers.verifiable import check_verifiable_facts


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_suite(path: Path) -> BenchmarkSuite:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return BenchmarkSuite.model_validate(raw)


def _git_sha() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=_repo_root(),
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def _parse_tool_output(text: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return None, f"json_decode_error: {e}"


async def _call_tool(task: BenchmarkTask) -> str:
    name = task.tool
    args = task.tool_args

    if name == "check_limitation":
        from src.tools.limitation_checker import check_limitation_period

        return await check_limitation_period(**args)
    if name == "search_precedents":
        from src.tools.precedent_search import search_precedents

        return await search_precedents(**args)
    if name == "find_case_laws":
        from src.tools.case_law_finder import find_case_laws

        return await find_case_laws(**args)
    if name == "legal_research":
        from src.tools.legal_research import conduct_legal_research

        return await conduct_legal_research(**args)
    if name == "analyze_document":
        from src.tools.document_analyzer import analyze_legal_document

        return await analyze_legal_document(**args)
    if name == "deep_research":
        from src.tools.deep_research import deep_research

        return await deep_research(**args)
    if name == "draft_legal_notice":
        from src.tools.document_drafter import draft_notice

        return await draft_notice(**args)

    raise ValueError(f"Unknown tool in benchmark registry: {name}")


def _percentile(sorted_vals: list[float], p: float) -> float | None:
    if not sorted_vals:
        return None
    k = (len(sorted_vals) - 1) * p / 100.0
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


async def run_tasks(
    tasks: list[BenchmarkTask],
    run_dir: Path,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    latencies_ms: list[float] = []
    fact_total = 0
    fact_pass = 0
    tasks_with_facts = 0
    tasks_all_facts_pass = 0
    errors = 0

    for task in tasks:
        t0 = time.perf_counter()
        err: str | None = None
        raw_text = ""
        try:
            raw_text = await _call_tool(task)
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
        latency_ms = (time.perf_counter() - t0) * 1000.0
        latencies_ms.append(latency_ms)

        parsed, parse_err = _parse_tool_output(raw_text) if raw_text else (None, "empty_output")
        if parse_err and err is None:
            err = parse_err

        fact_results: list[dict[str, Any]] = []
        all_facts_pass = True
        if task.verifiable_facts:
            tasks_with_facts += 1
            if parsed is None:
                all_facts_pass = False
                for vf in task.verifiable_facts:
                    fact_total += 1
                    fact_results.append(
                        {
                            "json_path": vf.json_path,
                            "passed": False,
                            "detail": f"no_json_parse: {parse_err or err}",
                        }
                    )
            else:
                fact_results, all_facts_pass = check_verifiable_facts(parsed, task.verifiable_facts)
                for fr in fact_results:
                    fact_total += 1
                    if fr["passed"]:
                        fact_pass += 1
            if all_facts_pass:
                tasks_all_facts_pass += 1

        if err is not None:
            errors += 1

        task_out = {
            "task_id": task.id,
            "tool": task.tool,
            "prompt": task.prompt,
            "scope": task.scope,
            "expected_tool": task.expected_tool,
            "rubric_id": task.rubric_id,
            "difficulty": task.difficulty,
            "domain_tags": task.domain_tags,
            "latency_ms": round(latency_ms, 2),
            "error": err,
            "raw_text": raw_text,
            "parsed": parsed,
            "verifiable_fact_results": fact_results,
            "all_verifiable_facts_passed": all_facts_pass if task.verifiable_facts else None,
        }
        out_path = run_dir / "per_task" / f"{task.id}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(task_out, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append(task_out)

    sorted_lat = sorted(latencies_ms)
    metrics = {
        "verifiable_accuracy": (
            tasks_all_facts_pass / tasks_with_facts if tasks_with_facts else None
        ),
        "verifiable_fact_pass_rate": (fact_pass / fact_total if fact_total else None),
        "citation_integrity": None,
        "tool_appropriateness": None,
        "latency_ms_p50": _percentile(sorted_lat, 50),
        "latency_ms_p95": _percentile(sorted_lat, 95),
        "error_rate": errors / len(tasks) if tasks else 0.0,
        "cost_usd_total": None,
        "counts": {
            "tasks": len(tasks),
            "tasks_with_verifiable_facts": tasks_with_facts,
            "tasks_all_verifiable_passed": tasks_all_facts_pass,
            "verifiable_facts_total": fact_total,
            "verifiable_facts_passed": fact_pass,
            "errors": errors,
        },
    }
    return {"rows": rows, "metrics_auto": metrics}


def _write_manifest(run_dir: Path, suite_path: Path, args: argparse.Namespace) -> None:
    manifest = {
        "run_id": run_dir.name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": _git_sha(),
        "suite_path": str(suite_path.resolve()),
        "offline": args.offline,
        "task_filter": args.task or [],
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )


def _write_rubric_csv(run_dir: Path, rows: list[dict[str, Any]]) -> None:
    path = run_dir / "human_rubric_queue.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "task_id",
                "prompt",
                "rubric_id",
                "system_label",
                "per_task_json_relpath",
                "notes",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    r["task_id"],
                    r["prompt"],
                    r["rubric_id"],
                    "Wakalat",
                    f"per_task/{r['task_id']}.json",
                    "",
                ]
            )


async def _async_main() -> int:
    root = _repo_root()
    sys.path.insert(0, str(root))

    parser = argparse.ArgumentParser(description="Wakalat MCP benchmark runner")
    parser.add_argument(
        "--suite",
        type=Path,
        default=root / "eval" / "benchmark_tasks.yaml",
        help="Path to benchmark_tasks.yaml",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "eval" / "runs",
        help="Directory for run artifacts",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip tasks with requires_network: true",
    )
    parser.add_argument(
        "--task",
        action="append",
        dest="task",
        default=[],
        help="Run only task id (repeatable)",
    )
    args = parser.parse_args()

    suite_path = args.suite
    if not suite_path.is_file():
        print(f"Suite not found: {suite_path}", file=sys.stderr)
        return 1

    suite = _load_suite(suite_path)
    tasks = list(suite.tasks)
    if args.offline:
        tasks = [t for t in tasks if not t.requires_network]
    if args.task:
        wanted = set(args.task)
        tasks = [t for t in tasks if t.id in wanted]
        missing = wanted - {t.id for t in tasks}
        if missing:
            print(f"Unknown task ids: {missing}", file=sys.stderr)
            return 1

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
    run_dir = args.output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    _write_manifest(run_dir, suite_path, args)
    result = await run_tasks(tasks, run_dir)

    (run_dir / "metrics_auto.json").write_text(
        json.dumps(result["metrics_auto"], indent=2),
        encoding="utf-8",
    )
    _write_rubric_csv(run_dir, result["rows"])

    print(json.dumps(result["metrics_auto"], indent=2))
    print(f"Artifacts written under {run_dir}")
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_async_main()))


if __name__ == "__main__":
    main()
