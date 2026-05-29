<div align="center">

# ThinkGraph

**Reasoning Trace Analysis Framework**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-25%20passed-brightgreen.svg)](tests/)

Turn the black-box reasoning process of LLMs into measurable, comparable, and optimizable data assets.

将大语言模型的黑盒推理过程转化为可测量、可对比、可优化的数据资产。

</div>

---

## 🎯 What It Does / 它能做什么

Input: Raw output text from thinking models (with `<think...>` blocks)
Output: Structured reasoning graph, quality scores, and interactive visualization

输入：Thinking Model 的原始输出文本（含推理块）
输出：结构化推理图谱、质量评分报告、可交互可视化

---

## ✨ Features / 功能特性

| Feature | Description |
|---------|-------------|
| **Trace Extraction** | Automatically detect `<think...>` and `<thinking...>` tags / 自动提取思维链标签 |
| **Step Segmentation** | Split reasoning into semantic steps by paragraphs, numbering, or pivots / 按语义边界切分推理步骤 |
| **Graph Construction** | Build directed reasoning graph with logical relations / 构建带逻辑关系的推理有向图 |
| **Quality Scoring** | 4-dimension scoring (Coherence, Efficiency, Depth, Confidence) + A/B/C/D grading / 四维质量评分 + 等级评定 |
| **Interactive Viz** | PyVis reasoning tree + Plotly radar/timeline charts / 交互式推理树 + 雷达图/时间线 |

---

## 📸 Demo / 演示

### Reasoning Tree / 推理树

![Reasoning Tree](assets/reasoning_tree.png)

### Quality Radar / 质量雷达图

![Metrics Radar](assets/metrics_radar.png)

### Step Timeline / 步骤时间线

![Step Timeline](assets/step_timeline.png)

### Cross-Model Comparison / 跨模型对比

![Comparison](assets/comparison.png)

---

## 🚀 Quick Start / 快速上手

### Installation / 安装

```bash
git clone https://github.com/Apageoflove/ThinkGraph.git
cd ThinkGraph
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -e ".[dev,demo]"
```

### Python API

```python
from thinkgraph import ThinkGraphAnalyzer

analyzer = ThinkGraphAnalyzer()
result = analyzer.analyze(open("response.txt").read(), model_name="deepseek-r1")

print(f"Score: {result.metrics['overall_score']}/100 ({result.metrics['grade']})")
print(f"Steps: {len(result.graph.steps)}")

analyzer.visualize(result, output_dir="./output")
```

### CLI / 命令行

```bash
# Analyze single model / 分析单个模型
thinkgraph analyze -i response.txt --model deepseek-r1 -o ./output

# Compare models / 对比模型
thinkgraph compare \
  -i r1.txt -i qwq.txt \
  -n DeepSeek-R1 -n QwQ-32B \
  -q "Solve x² - 5x + 6 = 0"

# JSON output / JSON 输出
thinkgraph analyze -i response.txt --json-output
```

### Gradio Demo / 可视化演示

```bash
python demo/app.py
# Open http://localhost:7860
```

---

## 🏗 Architecture / 架构

```
Raw Model Output / 原始模型输出
        │
        ▼
 ┌──────────────────┐
 │  TraceExtractor  │  Extract <think...> block / 提取推理块
 └────────┬─────────┘
          ▼
 ┌──────────────────┐
 │  StepSegmenter   │  Split into reasoning steps / 切分推理步骤
 └────────┬─────────┘
          ▼
 ┌──────────────────┐
 │ RelationDetector │  Detect step relations / 检测步骤关系
 └────────┬─────────┘
          ▼
 ┌──────────────────┐
 │   GraphBuilder   │  Build networkx DiGraph / 构建有向图
 └────────┬─────────┘
          ▼
 ┌──────────────────┐
 │  GraphAnalyzer   │  Compute graph features / 计算图特征
 └────────┬─────────┘
          ▼
 ┌──────────────────┐
 │  QualityScorer   │  Output quality metrics / 输出质量指标
 └────────┬─────────┘
          ▼
 ┌──────────────────┐
 │   Visualizer     │  Tree + Radar + Timeline / 可视化
 └──────────────────┘
```

---

## 📊 Metrics / 评分体系

| Metric 指标 | Weight 权重 | Description 说明 |
|:-----------:|:-----------:|:-----------------|
| **Coherence** 连贯性 | 30% | Logical consistency between steps / 步骤间逻辑连贯程度 |
| **Efficiency** 效率 | 25% | Reasoning efficiency (fewer backtracks = higher) / 推理效率（回溯越少越高） |
| **Depth** 深度 | 25% | Depth of reasoning chain / 推理链深度和层次 |
| **Confidence** 置信度 | 20% | Average step confidence / 步骤平均置信度 |

**Grading / 等级:** A (≥85) | B (≥70) | C (≥55) | D (<55)

---

## 📁 Project Structure / 项目结构

```
ThinkGraph/
├── thinkgraph/               # Core package / 核心包
│   ├── parser/               # Text parsing / 文本解析
│   │   ├── trace_extractor.py
│   │   ├── step_segmenter.py
│   │   └── relation_detector.py
│   ├── graph/                # Graph construction / 图构建
│   │   ├── models.py
│   │   ├── builder.py
│   │   └── analyzer.py
│   ├── metrics/              # Quality scoring / 质量评分
│   │   ├── quality_scorer.py
│   │   └── comparator.py
│   ├── visualizer/           # Visualization / 可视化
│   │   ├── graph_viz.py
│   │   └── report_viz.py
│   ├── analyzer.py           # Main entry / 主入口
│   └── cli.py                # CLI interface / 命令行接口
├── demo/
│   └── app.py                # Gradio demo
├── examples/
│   ├── sample_r1_output.txt
│   └── sample_qwq_output.txt
├── tests/                    # 25 test cases / 25 个测试用例
├── setup.py
├── requirements.txt
└── README.md
```

---

## 🧪 Run Tests / 运行测试

```bash
source venv/bin/activate
pytest tests/ -v
```

---

## 🗺 Roadmap / 计划

- [ ] Streaming input support / 支持 streaming 输入实时分析
- [ ] LLM-as-judge integration for better step classification / 集成 LLM 做更精准的分类
- [ ] Benchmark dataset and leaderboard / 推理质量 benchmark 数据集和排行榜

---

## 📄 License / 许可证

[MIT](LICENSE)
