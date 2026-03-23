# Wakalat MCP benchmark

Evaluation harness for **metrics** and **correctness** (golden tasks, automated checks, human rubric export). This is separate from pytest **tests** in `tests/`.

## Layout

| Path | Purpose |
|------|---------|
| [benchmark_tasks.yaml](benchmark_tasks.yaml) | Versioned task set (prompt, tool, args, verifiable facts, rubric id). |
| [metrics_spec.yaml](metrics_spec.yaml) | Metric definitions, aggregation, human rubric text. |
| [run_benchmark.py](run_benchmark.py) | CLI runner: calls tools, writes `metrics_auto.json`, per-task JSON, rubric CSV. |
| [models.py](models.py) | Pydantic schema for the YAML suite. |
| [scorers/](scorers/) | Automated scorers (verifiable JSON paths; extend with citation checks). |
| [templates/human_rubric_template.csv](templates/human_rubric_template.csv) | Blank sheet for annotators. |
| [NIYAM_BASELINE.md](NIYAM_BASELINE.md) | Head-to-head and blinded scoring protocol vs another product. |
| `runs/<run_id>/` | Generated artifacts (gitignored recommended). |

## Run

From repository root `Wakalat-AI-Backend/` (so `src` imports resolve):

```bash
# All tasks
python -m eval.run_benchmark

# Skip tasks that need network (Indian Kanoon, etc.)
python -m eval.run_benchmark --offline

# Single task
python -m eval.run_benchmark --task lim_money_lent_article
```

Outputs:

- `manifest.json` — time, git sha, suite path, flags.
- `metrics_auto.json` — verifiable accuracy, fact pass rate, latency percentiles, error rate (see metrics_spec).
- `per_task/<task_id>.json` — raw tool output, parsed JSON, fact-level results.
- `human_rubric_queue.csv` — queue for human scoring (Wakalat outputs; add Niyam manually per NIYAM_BASELINE.md).

## Metrics (summary)

- **verifiable_accuracy**: share of tasks with non-empty `verifiable_facts` where every fact passed.
- **verifiable_fact_pass_rate**: share of individual facts passed.
- **citation_integrity**: reserved; wire Indian Kanoon checks when tasks define citations.
- **tool_appropriateness**: reserved for end-to-end agent traces.
- **latency_ms_p50 / p95**: wall-clock per task.
- **error_rate**: tasks with tool exception, empty output, or JSON parse failure.

## Extending

1. Add rows to `benchmark_tasks.yaml` (keep `id` stable across releases or version the file).
2. Add scorers under `scorers/` and call them from `run_benchmark.py`.
3. For Gemini + MCP end-to-end, add a runner path that logs tool calls and fills `tool_appropriateness` using `expected_tool`.
