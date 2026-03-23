# Niyam AI (or any baseline) head-to-head protocol

Use the **same** `benchmark_tasks.yaml` prompts and the **same** human rubric (`legal_quality_v1` in [metrics_spec.yaml](metrics_spec.yaml)) so scores are comparable.

## 1. Capture baseline answers

1. For each task `id`, use the **prompt** field (lawyer-facing text) in Niyam’s UI or API.
2. Save the full answer text with metadata: date, model name if shown, and task `id`.
3. Add a column `system_label` = `Niyam` (or blinded `A` / `B` below).

If Niyam is UI-only, a spreadsheet with columns `task_id`, `prompt`, `answer_text`, `captured_at` is enough.

## 2. Blinded scoring (recommended)

1. For each task, pair **Wakalat** and **Niyam** outputs side by side.
2. Randomly assign labels **A** and **B** per task (record the mapping in a private `blinding_key.csv` not shared with annotators).
3. Annotators fill [templates/human_rubric_template.csv](templates/human_rubric_template.csv) (or the same columns) for **A** and **B** without knowing which system is which.
4. After scoring, merge with `blinding_key.csv` to compute win rate and average dimension scores per system.

## 3. Metrics to report

- **Mean / median** per rubric dimension (1–5) for each system.
- **Win rate**: on how many tasks did system X score higher on a weighted sum of dimensions (define weights once and keep fixed across runs).
- **Failure tags**: optional free-text categories (e.g. wrong statute, hallucinated citation, unsafe advice).

## 4. Automated metrics for Niyam

Only include automated checks (verifiable facts, citation integrity) if you can run the **same** checks on exported Niyam text (e.g. regex or re-parse citations). Do not treat an LLM judge as ground truth for legal correctness.

## 5. Comparing runs

Fix a **benchmark version** (commit hash or `benchmark_tasks.yaml` checksum). When you change tasks or rubric definitions, bump version and do not compare raw scores across versions without recalibrating.
