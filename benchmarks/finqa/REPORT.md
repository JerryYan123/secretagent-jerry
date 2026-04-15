# FinQA Benchmark Report

## Dataset

[FinQA](https://aclanthology.org/2021.emnlp-main.300) (Chen et al., EMNLP 2021): numerical reasoning over financial reports.
Each instance provides surrounding text, a markdown table from an SEC filing, and a question requiring arithmetic or percentage reasoning.

| Split | Source file | Cases | Labels |
|-------|-------------|-------|--------|
| train | `train.json` | ~6,251 | yes |
| valid (dev) | `dev.json` | ~883 | yes |
| test | `test.json` | ~1,147 | yes |

Gold answers are floats (`exe_ans`) representing exact numeric results.

## Experiment Conditions

| Condition | Config | Method | Description |
|-----------|--------|--------|-------------|
| Unstructured baseline | `conf/zeroshot_prompt.yaml` | `prompt_llm` | Single-shot custom prompt template, raw string output. |
| Structured baseline | `conf/conf.yaml` | `simulate` | Framework structured prompt (SimulateFactory). |
| PoT v1 | `conf/pot.yaml` (old) | `program_of_thought` | LLM writes Python in sandbox. No tools, `inject_args=true`. |
| PoT v2 | `conf/pot.yaml` | `program_of_thought` | LLM writes Python with `parse_table` and `compute` tools + `re` import. |
| Workflow v1 | `conf/workflow.yaml` (old) | `direct` chain | 3-step LLM pipeline: state goal → list numbers → synthesize answer. |
| Workflow v2 | `conf/workflow.yaml` | `direct` chain | LLM extracts reasoning plan (target + formula); Python evaluates the formula. Falls back to LLM extraction. |
| ReAct v2 | `conf/react.yaml` | `simulate_pydantic` | Pydantic-ai agent with grounded tools: `parse_table`, `lookup_cell`, `compute` (all `direct` Python) + `extract_reasoning_plan` (LLM). |

Default model: `together_ai/deepseek-ai/DeepSeek-V3.1` (all conditions).

## Results (valid split, N=300)

| Condition | Accuracy | Cost/ex | Latency/ex | Exceptions | Status |
|-----------|----------|---------|------------|------------|--------|
| **Simulate (baseline)** | **68.3%** | $0.0010 | 4.2s | 0 | done |
| Workflow v2 (plan+compute) | 65.7% | $0.0012 | 4.9s | 0 | done |
| Workflow v1 (3-LLM) | 62.7% | $0.0031 | 21.1s | 0 | done |
| Zeroshot prompt | 56.0% | $0.0006 | 0.6s | 0 | done |
| PoT v1 (no tools) | 49.7% | $0.0013 | 33.8s | 23 | done |
| ReAct v2 (grounded) | 49.0% | $0.0088 | 265.8s | 0 | done |
| PoT v2 (with tools) | 44.3% | $0.0017 | 16.6s | 17 | done |

![Accuracy vs Cost](results_plot.png)

## Analysis

### Simulate remains the strongest single-call approach

The framework's structured `simulate` prompt (68.3%) continues to outperform all other strategies. It benefits from the `<answer>` tag format that focuses the model's output and avoids verbose reasoning that can dilute accuracy.

### Workflow v2 improved over v1 (+3.0 pp, 2.5x cheaper)

The redesigned workflow — where the LLM produces a reasoning plan with an explicit formula and Python's `compute()` evaluates it — outperforms the v1 3-LLM pipeline (65.7% vs 62.7%). It's also 2.5x cheaper ($0.0012 vs $0.0031) and 4x faster (4.9s vs 21.1s) because it makes fewer LLM calls: one `extract_reasoning_plan` call plus an optional `extract_final_number` fallback, versus three sequential `simulate` calls.

The key architectural insight: separating *what to compute* (LLM judgment) from *doing the computation* (Python arithmetic) is more effective than chaining multiple LLM calls that rephrase each other.

### ReAct is expensive and underperforms

Despite having grounded tools (`parse_table`, `lookup_cell`, `compute`), the ReAct agent (49.0%) underperforms even the zeroshot baseline. Two issues:

1. **DeepSeek-V3.1 tool-use reliability**: The model sometimes emits raw tool-call tokens instead of properly invoking tools through the pydantic-ai API, producing garbage output.
2. **Overhead vs. benefit**: The agent loop averages $0.0088/ex and 265.8s latency — 9x the cost and 63x the latency of simulate — for worse accuracy. The model doesn't effectively leverage the grounded tools to improve over its single-call reasoning.

### PoT continues to struggle

Both PoT variants underperform: v1 (49.7%) and v2 (44.3%). The v2 change (adding `parse_table` and `compute` as tools) actually hurt — the model may be confused by tool availability in the code-generation prompt. The primary failure mode remains the model generating prose instead of a Python code block, causing extraction failures (17–23 exceptions out of 300).

### Error analysis (from earlier 64-case ReAct run)

A detailed error analysis of an earlier ReAct run revealed three failure categories:

| Category | Count | Description |
|----------|-------|-------------|
| Tool-call leaks | 7/35 | Model emits raw `<tool_calls_begin>` tokens |
| Format mismatch | 14/35 | Correct number computed but lost in verbose output |
| Wrong computation | 14/35 | Actual arithmetic or reasoning errors |

The **format mismatch** issue was partially addressed by improving the evaluator's `normalize_finqa_prediction` to prefer the first numeric line over the last line, and by teaching `_to_float_token` to strip unit words like "million". These evaluator fixes benefit all conditions equally.

## Scoring

`FinQAEvaluator` in `evaluator.py`: numeric-tolerant matching with `rel_tol=2e-3`.
Handles `%` vs decimal gold (e.g. prediction `93.5%` matches gold `0.935`), `<answer>` tag stripping,
currency symbol removal (`$`, `€`, `£`), unit word stripping (`million`, `billion`),
and multi-line output normalization (prefers first numeric line).

## Ptool Design

### Grounded tools (direct Python, no LLM)

- **`parse_table(problem)`**: Extracts the markdown table into clean tab-separated text.
- **`lookup_cell(problem, row_label, column)`**: Fuzzy row/column lookup returning exact cell values.
- **`compute(expression)`**: Safe arithmetic evaluation with `$`/`,` stripping.

### LLM reasoning tools (simulate)

- **`extract_reasoning_plan(problem)`**: Produces a structured plan (target, values with row/col refs, formula with numbers substituted).
- **`extract_final_number(verbose_output)`**: Cleans verbose LLM output to a bare number.

### Design principle

Following the pattern established by the strongest benchmarks in the framework (RuleArena's L1 extract-then-compute, TabMWP's direct table tools): the LLM handles *understanding and planning* while Python handles *data retrieval and arithmetic*. This avoids LLM-to-LLM passthroughs that add cost and error propagation without adding grounding.

## Reproducing

```bash
cd benchmarks/finqa

# Run each condition
uv run python expt.py run --config-file conf/conf.yaml evaluate.expt_name=simulate dataset.n=300
uv run python expt.py run --config-file conf/zeroshot_prompt.yaml evaluate.expt_name=zeroshot_prompt dataset.n=300
uv run python expt.py run --config-file conf/pot.yaml evaluate.expt_name=pot dataset.n=300
uv run python expt.py run --config-file conf/workflow.yaml evaluate.expt_name=workflow dataset.n=300
uv run python expt.py run --config-file conf/react.yaml evaluate.expt_name=react dataset.n=300

# Analyze results
uv run -m secretagent.cli.results average --latest 1 --metric correct --metric cost- results/*/
uv run -m secretagent.cli.results plot --latest 1 --metric cost- --metric correct --output results_plot.png results/*/

# Export to shared results directory
uv run -m secretagent.cli.results export --latest 1 results/*/
```
