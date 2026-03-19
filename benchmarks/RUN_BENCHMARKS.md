# 如何跑通 Sports 和 MUSR Benchmark

**不修改任何代码**，按以下步骤即可运行。

---

## 前置条件

- 已安装依赖：`uv sync`（在项目根目录 secretagent/ 下）
- Sports / MUSR 使用 Claude：需设置 `ANTHROPIC_API_KEY`

---

## 1. Sports Understanding

**必须在 `benchmarks/sports_understanding/` 目录下运行**，并设置 `PYTHONPATH`：

```bash
cd /Users/yanjiarui/Desktop/Will_research/secretagent/benchmarks/sports_understanding

# 快速测试（1 个样本）
PYTHONPATH=../../src uv run python expt.py quick-test ptools.are_sports_in_sentence_consistent.method=simulate

# 正式 run（可加 dataset.n=2 做快速验证）
PYTHONPATH=../../src uv run python expt.py run evaluate.expt_name=workflow dataset.n=2 \
  ptools.are_sports_in_sentence_consistent.method=direct \
  ptools.are_sports_in_sentence_consistent.fn=ptools.sports_understanding_workflow
```

**5 种实验条件**（参考 Makefile）：

| 条件 | 命令 |
|------|------|
| workflow | `... run evaluate.expt_name=workflow ptools.are_sports_in_sentence_consistent.method=direct ptools.are_sports_in_sentence_consistent.fn=ptools.sports_understanding_workflow` |
| pot | `... run evaluate.expt_name=pot ptools.are_sports_in_sentence_consistent.method=program_of_thought ptools.are_sports_in_sentence_consistent.tools=[ptools.analyze_sentence,ptools.sport_for,ptools.consistent_sports]` |
| react | `... run evaluate.expt_name=react ptools.are_sports_in_sentence_consistent.method=simulate_pydantic ptools.are_sports_in_sentence_consistent.tools=[ptools.analyze_sentence,ptools.sport_for,ptools.consistent_sports]` |
| zeroshot_structured | `... run evaluate.expt_name=zeroshot_structured ptools.are_sports_in_sentence_consistent.method=simulate` |
| zeroshot_unstructured | `... run evaluate.expt_name=zeroshot_unstructured ptools.are_sports_in_sentence_consistent.method=direct ptools.are_sports_in_sentence_consistent.fn=ptools.zeroshot_unstructured_workflow` |

---

## 2. MUSR

**在项目根目录 `secretagent/` 下运行**。MUSR 的 expt.py 已内置 `sys.path`，无需 `PYTHONPATH`。

### 2.1 首次运行：下载数据

```bash
cd /Users/yanjiarui/Desktop/Will_research/secretagent
uv run benchmarks/musr/data/download.py
```

### 2.2 运行 3 种任务

```bash
cd /Users/yanjiarui/Desktop/Will_research/secretagent

# Murder mysteries
uv run python benchmarks/musr/expt.py run --config-file conf/murder.yaml dataset.n=2

# Object placements
uv run python benchmarks/musr/expt.py run --config-file conf/object.yaml dataset.n=2

# Team allocation
uv run python benchmarks/musr/expt.py run --config-file conf/team.yaml dataset.n=2
```

注意：`--config-file` 的路径是相对于 `benchmarks/musr/` 的，即 `conf/murder.yaml` 等。

### 2.3 不同方法（workflow / zeroshot / agent）

```bash
# Zeroshot
uv run python benchmarks/musr/expt.py run --config-file conf/murder.yaml \
  ptools.answer_question.method=simulate evaluate.expt_name=murder_zeroshot dataset.n=2

# Agent (PoT)
uv run python benchmarks/musr/expt.py run --config-file conf/murder.yaml \
  ptools.answer_question.method=program_of_thought evaluate.expt_name=murder_agent dataset.n=2
```

---

## 3. 查看结果

结果保存在各 benchmark 的 `results/` 目录下：

- Sports: `benchmarks/sports_understanding/results/`
- MUSR: `benchmarks/musr/results/`

```bash
# 列出并汇总
uv run python -m secretagent.cli.results list results/*
uv run python -m secretagent.cli.results average --metric correct --metric cost results/*
```

---

## 总结

| Benchmark | 工作目录 | 特殊设置 | 数据准备 |
|-----------|----------|----------|----------|
| **Sports** | `benchmarks/sports_understanding/` | `PYTHONPATH=../../src` | 已有 valid.json |
| **MUSR** | `secretagent/`（项目根） | 无 | 需先运行 `download.py` |
