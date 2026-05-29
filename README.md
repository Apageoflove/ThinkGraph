<div align="center">

<br>

# 🔬 ThinkGraph

### Reasoning Trace Analysis Framework

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-25_passed-brightgreen?style=for-the-badge)](tests/)

**Turn the black-box reasoning process of LLMs into measurable, comparable, and optimizable data assets.**

将大语言模型的黑盒推理过程转化为可测量、可对比、可优化的数据资产。

<br>

<p align="center">
  <img src="assets/reasoning_tree.png" width="100%" alt="Reasoning Tree">
</p>

<br>

</div>

---

## 📖 Overview

| | Description |
|:---:|:---|
| **Input** | Raw output text from thinking models (with `<think...>` blocks) |
| **Output** | Structured reasoning graph, quality scores, and interactive visualization |
| **输入** | Thinking Model 的原始输出文本（含推理块） |
| **输出** | 结构化推理图谱、质量评分报告、可交互可视化 |

---

## ✨ Features

| # | Feature | Description |
|:---:|:--------|:------------|
| 1 | **Trace Extraction** | Automatically detect and extract `<think...>` / `<thinking...>` blocks |
| 2 | **Step Segmentation** | Split reasoning into semantic steps by paragraphs, numbering, or pivot words |
| 3 | **Graph Construction** | Build directed reasoning graph with logical relations (supports / contradicts / extends / backtracks / concludes) |
| 4 | **Quality Scoring** | 4-dimension scoring + A/B/C/D grading system |
| 5 | **Interactive Visualization** | PyVis reasoning tree + Plotly radar chart / timeline / comparison charts |
| 6 | **Cross-Model Comparison** | Side-by-side analysis of outputs from different thinking models |
| 7 | **CLI & API** | Full command-line interface and Python API |

---

## 📸 Gallery

<table>
<tr>
<td align="center" width="50%">
<img src="assets/reasoning_tree.png" width="100%"/><br>
<b>Reasoning Trace Graph</b>
</td>
<td align="center" width="50%">
<img src="assets/metrics_radar.png" width="100%"/><br>
<b>Quality Metrics Radar</b>
</td>
</tr>
<tr>
<td align="center">
<img src="assets/step_timeline.png" width="100%"/><br>
<b>Step Confidence Timeline</b>
</td>
<td align="center">
<img src="assets/comparison.png" width="100%"/><br>
<b>Cross-Model Comparison</b>
</td>
</tr>
<tr>
<td colspan="2" align="center">
<img src="assets/report_card.png" width="100%"/><br>
<b>Quality Report Card</b>
</td>
</tr>
</table>

---

## 📊 Metrics System

| Metric | Weight | Formula | Description |
|:------:|:------:|:--------|:------------|
| **Coherence** | 30% | edge_count / node_count ratio | Logical consistency between reasoning steps |
| **Efficiency** | 25% | 100 - backtrack_ratio | Fewer backtracks = higher efficiency |
| **Depth** | 25% | max_depth / total_steps | Depth and hierarchy of reasoning chain |
| **Confidence** | 20% | average step confidence | Mean confidence level across all steps |

**Grading Scale:**

| Grade | Score Range | Interpretation |
|:-----:|:-----------:|:---------------|
| **A** | 85 - 100 | Excellent reasoning quality |
| **B** | 70 - 84 | Good with minor issues |
| **C** | 55 - 69 | Acceptable, needs improvement |
| **D** | 0 - 54 | Significant reasoning issues |

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/Apageoflove/ThinkGraph.git
cd ThinkGraph
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -e ".[dev,demo]"
```

### Python API (5 lines)

```python
from thinkgraph import ThinkGraphAnalyzer

analyzer = ThinkGraphAnalyzer()
result = analyzer.analyze(open("response.txt").read(), model_name="deepseek-r1")

print(result.metrics)          # -> {'overall_score': 72.5, 'grade': 'B', ...}
analyzer.visualize(result)     # -> generates HTML + PNG files
```

### CLI

```bash
# Analyze a single model
thinkgraph analyze -i response.txt --model deepseek-r1 -o ./output

# Compare two models side by side
thinkgraph compare \
  -i r1_output.txt -i qwq_output.txt \
  -n DeepSeek-R1 -n QwQ-32B \
  -q "Solve x^2 - 5x + 6 = 0"

# Get JSON output
thinkgraph analyze -i response.txt --json-output
```

**Example output:**

```
Model: deepseek-r1
Steps: 3
Score: 53.7 (D)

Issues:
  - Reasoning chain too shallow (depth 0)
  - No verification step detected

Strengths:
  - No backtracking detected, reasoning is linear
  - High overall confidence
```

### Gradio Web Demo

```bash
python demo/app.py
# Open http://localhost:7860 in browser
```

Paste any thinking model output, get real-time reasoning tree + metrics.

---

## 🏗 Architecture

```
Raw Model Output
       |
       v
+------------------+
|  TraceExtractor  |    Extract <think...> block
+--------+---------+
         |
         v
+------------------+
|  StepSegmenter   |    Split into ReasoningStep list
+--------+---------+
         |
         v
+------------------+
| RelationDetector |    Detect logical relations between steps
+--------+---------+
         |
         v
+------------------+
|   GraphBuilder   |    Build networkx DiGraph
+--------+---------+
         |
         v
+------------------+
|  GraphAnalyzer   |    Compute graph structural features
+--------+---------+
         |
         v
+------------------+
|  QualityScorer   |    Output quality metrics
+--------+---------+
         |
         v
+------------------+
|   Visualizer     |    Interactive tree + charts
+------------------+
```

---

## 📁 Project Structure

```
ThinkGraph/
├── thinkgraph/                   # Core package
│   ├── parser/
│   │   ├── trace_extractor.py    # Extract thinking blocks
│   │   ├── step_segmenter.py     # Segment into reasoning steps
│   │   └── relation_detector.py  # Detect step relations
│   ├── graph/
│   │   ├── models.py             # Data structures (dataclass)
│   │   ├── builder.py            # Build networkx DiGraph
│   │   └── analyzer.py           # Graph structural analysis
│   ├── metrics/
│   │   ├── quality_scorer.py     # 4-dimension quality scoring
│   │   └── comparator.py         # Cross-model comparison
│   ├── visualizer/
│   │   ├── graph_viz.py          # PyVis + matplotlib tree
│   │   └── report_viz.py         # Plotly radar / timeline / bar
│   ├── analyzer.py               # Unified entry point
│   └── cli.py                    # Click CLI interface
├── demo/
│   └── app.py                    # Gradio web demo
├── examples/
│   ├── sample_r1_output.txt      # DeepSeek-R1 sample
│   └── sample_qwq_output.txt     # QwQ-32B sample
├── tests/                        # 25 test cases
├── setup.py
└── requirements.txt
```

---

## 🧪 Run Tests

```bash
source venv/bin/activate
pytest tests/ -v

# Expected output:
# ============================= test session starts ==============================
# tests/test_parser.py::TestTraceExtractor::test_extract_think_tags PASSED
# tests/test_parser.py::TestStepSegmenter::test_segment_steps PASSED
# tests/test_graph.py::TestGraphBuilder::test_build_graph PASSED
# tests/test_metrics.py::TestQualityScorer::test_scorer_output_fields PASSED
# ...
# ============================== 25 passed in 1.46s =============================
```

---

## 🔧 Tech Stack

| Component | Technology |
|:---------:|:----------:|
| Graph | [networkx](https://networkx.org/) |
| Interactive Tree | [pyvis](https://pyvis.readthedocs.io/) |
| Static Charts | [matplotlib](https://matplotlib.org/) |
| Dynamic Charts | [plotly](https://plotly.com/python/) |
| Web Demo | [gradio](https://gradio.app/) |
| Data | [pandas](https://pandas.pydata.org/) |
| CLI | [click](https://click.palletsprojects.com/) |

---

## 🗺 Roadmap

- [ ] Streaming input support for real-time analysis
- [ ] LLM-as-judge integration for smarter step classification
- [ ] Benchmark dataset and public leaderboard

---

## 📄 License

[MIT](LICENSE)
