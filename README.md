<div align="center">

🌐 **[English](#english)** · **[中文](#chinese)**

</div>

<a id="english"></a>
<div align="center">

<br>

# 🔬 ThinkGraph

### Reasoning Trace Analysis Framework

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-25_passed-brightgreen?style=for-the-badge)](tests/)
[![中文文档](https://img.shields.io/badge/README-中文版-FF6B6B?style=for-the-badge)](#-中文版)

**Turn the black-box reasoning process of LLMs into measurable, comparable, and optimizable data assets.**

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

# Expected: 25 passed
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

---
---

<br>

<div align="center">

# 🔬 ThinkGraph

### 推理轨迹分析框架

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-25_passed-brightgreen?style=for-the-badge)](tests/)
[![English](https://img.shields.io/badge/README-English-3B82F6?style=for-the-badge)](#-thinkgraph)

**将大语言模型的黑盒推理过程转化为可测量、可对比、可优化的数据资产。**

<br>

</div>

---

<a id="chinese"></a>

## 📖 项目简介

ThinkGraph 是一个针对 thinking model（DeepSeek-R1、QwQ-32B、Claude 等）推理轨迹的结构化解析、质量分析与可视化框架。

| | 说明 |
|:---:|:-----|
| **输入** | Thinking Model 的原始输出文本（含 `<think...>` 标签） |
| **输出** | 结构化推理图谱、质量评分报告、可交互可视化图表 |

---

## ✨ 功能特性

| # | 功能 | 说明 |
|:---:|:-----|:-----|
| 1 | **推理轨迹提取** | 自动识别并提取 `<think...>` / `<thinking...>` 标签中的思维链内容 |
| 2 | **语义步骤切分** | 按段落边界、显式编号、转折词等将推理过程分割为有序步骤 |
| 3 | **推理图谱构建** | 检测步骤间逻辑关系（支持/反驳/延伸/回溯/结论），构建有向图 |
| 4 | **质量评分** | 四维评分体系 + A/B/C/D 等级评定 |
| 5 | **交互式可视化** | PyVis 推理树 + Plotly 雷达图/时间线/对比图 |
| 6 | **跨模型对比** | 两个模型的推理输出并排分析 |
| 7 | **命令行 & API** | 完整的 CLI 工具和 Python API 接口 |

---

## 📸 效果展示

<table>
<tr>
<td align="center" width="50%">
<img src="assets/reasoning_tree.png" width="100%"/><br>
<b>推理轨迹图谱</b>
</td>
<td align="center" width="50%">
<img src="assets/metrics_radar.png" width="100%"/><br>
<b>质量指标雷达图</b>
</td>
</tr>
<tr>
<td align="center">
<img src="assets/step_timeline.png" width="100%"/><br>
<b>步骤置信度时间线</b>
</td>
<td align="center">
<img src="assets/comparison.png" width="100%"/><br>
<b>跨模型对比</b>
</td>
</tr>
<tr>
<td colspan="2" align="center">
<img src="assets/report_card.png" width="100%"/><br>
<b>质量报告卡</b>
</td>
</tr>
</table>

---

## 📊 评分体系

| 指标 | 权重 | 计算方式 | 说明 |
|:----:|:----:|:---------|:-----|
| **连贯性** | 30% | 边数 / 节点数 比值 | 步骤间逻辑连贯程度 |
| **效率** | 25% | 100 - 回溯比例 | 回溯越少效率越高 |
| **深度** | 25% | 最长路径 / 总步骤数 | 推理链的层次深度 |
| **置信度** | 20% | 步骤平均置信度 | 整体确定性水平 |

**等级划分：**

| 等级 | 分数范围 | 含义 |
|:----:|:--------:|:-----|
| **A** | 85 - 100 | 推理质量优秀，逻辑清晰 |
| **B** | 70 - 84 | 整体良好，有少量问题 |
| **C** | 55 - 69 | 可接受，有明显改进空间 |
| **D** | 0 - 54 | 推理质量较差，问题较多 |

---

## 🚀 快速上手

### 安装

```bash
git clone https://github.com/Apageoflove/ThinkGraph.git
cd ThinkGraph
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -e ".[dev,demo]"
```

### Python API（5 行代码）

```python
from thinkgraph import ThinkGraphAnalyzer

analyzer = ThinkGraphAnalyzer()
result = analyzer.analyze(open("response.txt").read(), model_name="deepseek-r1")

print(result.metrics)          # -> {'overall_score': 72.5, 'grade': 'B', ...}
analyzer.visualize(result)     # -> 生成 HTML + PNG 可视化文件
```

### 命令行

```bash
# 分析单个模型
thinkgraph analyze -i response.txt --model deepseek-r1 -o ./output

# 对比两个模型
thinkgraph compare \
  -i r1_output.txt -i qwq_output.txt \
  -n DeepSeek-R1 -n QwQ-32B \
  -q "解方程 x^2 - 5x + 6 = 0"

# JSON 格式输出
thinkgraph analyze -i response.txt --json-output
```

**输出示例：**

```
模型: deepseek-r1
推理步骤数: 3
综合评分: 53.7 (D)

问题:
  - 推理链过浅（深度仅为 0）
  - 缺少验证步骤

优势:
  - 推理过程无回溯，思路清晰
  - 整体置信度较高
```

### Gradio 网页演示

```bash
python demo/app.py
# 浏览器打开 http://localhost:7860
```

粘贴模型输出文本，实时生成推理树和指标面板。

---

## 🏗 架构流程

```
原始模型输出
     │
     ▼
┌──────────────────┐
│  TraceExtractor   │    提取 <think...> 推理块
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  StepSegmenter    │    切分为推理步骤列表
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ RelationDetector  │    检测步骤间逻辑关系
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   GraphBuilder    │    构建 networkx 有向图
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  GraphAnalyzer    │    计算图结构特征
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  QualityScorer    │    输出质量指标
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Visualizer      │    推理树 + 图表可视化
└──────────────────┘
```

---

## 📁 项目结构

```
ThinkGraph/
├── thinkgraph/                   # 核心代码包
│   ├── parser/                   #   文本解析模块
│   │   ├── trace_extractor.py    #     提取推理块
│   │   ├── step_segmenter.py     #     切分推理步骤
│   │   └── relation_detector.py  #     检测步骤关系
│   ├── graph/                    #   图构建模块
│   │   ├── models.py             #     数据结构定义
│   │   ├── builder.py            #     构建有向图
│   │   └── analyzer.py           #     图结构分析
│   ├── metrics/                  #   评分模块
│   │   ├── quality_scorer.py     #     质量评分
│   │   └── comparator.py         #     模型对比
│   ├── visualizer/               #   可视化模块
│   │   ├── graph_viz.py          #     推理树图
│   │   └── report_viz.py         #     指标图表
│   ├── analyzer.py               #   统一入口
│   └── cli.py                    #   命令行接口
├── demo/
│   └── app.py                    # Gradio 网页演示
├── examples/
│   ├── sample_r1_output.txt      # DeepSeek-R1 示例
│   └── sample_qwq_output.txt     # QwQ-32B 示例
├── tests/                        # 25 个测试用例
├── setup.py
└── requirements.txt
```

---

## 🧪 运行测试

```bash
source venv/bin/activate
pytest tests/ -v

# 预期结果: 25 passed
```

---

## 🔧 技术栈

| 组件 | 技术 |
|:----:|:----:|
| 图数据结构 | [networkx](https://networkx.org/) |
| 交互式推理树 | [pyvis](https://pyvis.readthedocs.io/) |
| 静态图表 | [matplotlib](https://matplotlib.org/) |
| 动态图表 | [plotly](https://plotly.com/python/) |
| 网页演示 | [gradio](https://gradio.app/) |
| 数据处理 | [pandas](https://pandas.pydata.org/) |
| 命令行 | [click](https://click.palletsprojects.com/) |

---

## 🗺 开发计划

- [ ] 支持 streaming 输入实时分析
- [ ] 集成 LLM-as-judge 做更精准的步骤分类
- [ ] 推理质量 benchmark 数据集和排行榜

---

## 📄 许可证

[MIT](LICENSE)
