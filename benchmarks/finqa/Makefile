# FinQA — run from benchmarks/finqa
#
# Override model / size:
#   make react MODEL=claude-haiku-4-5-20251001 N=100
#
# Data (large; gitignored): make download && make build

MODEL ?= together_ai/deepseek-ai/DeepSeek-V3.1
N ?= 300

DOT_N := $(if $(N),dataset.n=$(N),)

.PHONY: download build build-small help \
	simulate zeroshot-prompt pot react workflow quick-test \
	test export \
	list avg compare costs

help:
	@echo "Data:  download | build | build-small"
	@echo ""
	@echo "Spreadsheet columns (all on valid split):"
	@echo "  Unst    = make zeroshot-prompt"
	@echo "  Str     = make simulate"
	@echo "  PoT     = make pot"
	@echo "  ReAct   = make react"
	@echo "  WFlow   = make workflow"
	@echo "  Export  = make export"
	@echo "  Report  = REPORT.md"
	@echo "  Test    = make test"
	@echo ""
	@echo "Debug: quick-test | Meta: list | avg | compare | costs"
	@echo "Vars:  MODEL=$(MODEL)  N=$(N) (default 300; N= for full split)"

download:
	uv run python data/download.py

build:
	uv run python data/build_datasets.py

build-small:
	uv run python data/build_datasets.py --max-per-split 30

# --- Spreadsheet experiment columns ---

# Str: structured baseline
simulate:
	uv run python expt.py run --config-file conf/conf.yaml \
	  evaluate.expt_name=simulate llm.model=$(MODEL) $(DOT_N)

# Unst: unstructured baseline
zeroshot-prompt:
	uv run python expt.py run --config-file conf/zeroshot_prompt.yaml \
	  evaluate.expt_name=zeroshot_prompt llm.model=$(MODEL) $(DOT_N)

# PoT: program of thought
pot:
	uv run python expt.py run --config-file conf/pot.yaml \
	  evaluate.expt_name=pot llm.model=$(MODEL) $(DOT_N)

# ReAct: pydantic-ai agent with tools
react:
	uv run python expt.py run --config-file conf/react.yaml \
	  evaluate.expt_name=react llm.model=$(MODEL) $(DOT_N)

# WFlow: fixed 3-step pipeline
workflow:
	uv run python expt.py run --config-file conf/workflow.yaml \
	  evaluate.expt_name=workflow llm.model=$(MODEL) $(DOT_N)

quick-test:
	uv run python expt.py quick-test --config-file conf/conf.yaml \
	  dataset.n=1 llm.model=$(MODEL)

# --- Checklist columns ---

# Test: pytest suite in benchmarks/tests/
test:
	cd ../tests && uv run python -m pytest test_finqa.py -v

# Export: copy results to benchmarks/results/ (tracked in git)
export:
	uv run python -m secretagent.cli.results export --as finqa results/*

# --- Summarize past runs ---

list:
	uv run python -m secretagent.cli.results list results/*

avg:
	uv run python -m secretagent.cli.results average --metric correct --metric cost results/*

compare:
	uv run python -m secretagent.cli.results compare-configs results/*

costs:
	uv run python -m secretagent.cli.costs llm_cache
