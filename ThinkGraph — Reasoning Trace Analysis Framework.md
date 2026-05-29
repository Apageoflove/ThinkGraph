# ThinkGraph — Reasoning Trace Analysis Framework
# Agent 完整构建需求文档 v1.0

---

## 0. 项目定位

ThinkGraph 是一个针对 thinking model（DeepSeek-R1、QwQ-32B、Claude 等）
推理轨迹的结构化解析、质量分析与可视化框架。

核心价值：将 <think> 块中的非结构化推理文本转化为
可量化的推理图谱与质量指标体系。

---

## 1. 项目目录结构（必须严格按此建立）

```
thinkgraph/
├── thinkgraph/
│   ├── __init__.py
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── trace_extractor.py     # 提取<think>块原始文本
│   │   ├── step_segmenter.py      # 将推理文本切分为步骤列表
│   │   └── relation_detector.py   # 检测步骤间逻辑关系
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── builder.py             # 构建推理有向图(networkx)
│   │   ├── analyzer.py            # 图结构分析算法
│   │   └── models.py              # 数据结构定义(dataclass)
│   ├── metrics/
│   │   ├── __init__.py
│   │   ├── quality_scorer.py      # 推理质量指标计算
│   │   └── comparator.py          # 跨模型对比分析
│   ├── visualizer/
│   │   ├── __init__.py
│   │   ├── graph_viz.py           # pyvis/matplotlib推理树可视化
│   │   └── report_viz.py          # 指标报告可视化(plotly)
│   └── analyzer.py                # 统一入口 ThinkGraphAnalyzer
├── demo/
│   └── app.py                     # Gradio Demo
├── examples/
│   ├── sample_r1_output.txt       # DeepSeek-R1 示例输出
│   ├── sample_qwq_output.txt      # QwQ 示例输出
│   └── quickstart.ipynb           # Jupyter 快速上手
├── tests/
│   ├── test_parser.py
│   ├── test_graph.py
│   └── test_metrics.py
├── benchmarks/
│   └── model_comparison.py        # 跨模型benchmark脚本
├── requirements.txt
├── setup.py
└── README.md
```

---

## 2. 数据流（全局）

```
原始模型输出文本
    ↓
[trace_extractor]   提取 <think>...</think> 原始内容
    ↓
[step_segmenter]    按语义边界切分为 Step 列表
    ↓
[relation_detector] 识别步骤间关系（支持/反驳/延伸/回溯/结论）
    ↓
[graph.builder]     构建 networkx DiGraph
    ↓
[graph.analyzer]    计算图结构特征
    ↓
[metrics.quality_scorer] 输出质量指标 dict
    ↓
[visualizer]        推理树图 + 指标面板
```

---

## 3. 各模块详细实现要求

### 3.1 parser/trace_extractor.py

功能：从原始文本中提取推理轨迹内容

```python
class TraceExtractor:
    def extract(self, raw_text: str) -> str:
        """
        支持以下格式：
        1. <think>...</think> 标签包裹
        2. <thinking>...</thinking> 标签包裹
        3. 无标签时返回全文
        返回：纯推理文本字符串
        """

    def has_thinking_trace(self, raw_text: str) -> bool:
        """判断文本是否包含思维链标签"""
```

### 3.2 parser/step_segmenter.py

功能：将推理文本切分为语义步骤

切分规则（按优先级）：
1. 显式编号：`1.` `Step 1:` `首先` `然后` `最后`
2. 段落边界：连续两个换行
3. 语义转折词：`但是` `however` `wait` `actually` `let me reconsider`
4. 最小步骤长度：20字符；最大：500字符

```python
@dataclass
class ReasoningStep:
    step_id: int
    content: str
    step_type: str   # "hypothesis"|"deduction"|"backtrack"|"verification"|"conclusion"
    confidence: float  # 0-1，基于关键词判断
    char_count: int

class StepSegmenter:
    def segment(self, trace_text: str) -> List[ReasoningStep]:
        """返回有序步骤列表"""

    def _classify_step_type(self, text: str) -> str:
        """
        backtrack 关键词: wait, actually, no, let me reconsider,
                          等等, 不对, 重新, 让我重新
        hypothesis 关键词: assume, suppose, if, 假设, 如果
        conclusion 关键词: therefore, so, thus, 因此, 所以, 综上
        verification 关键词: check, verify, 验证, 检查, 确认
        其余默认: deduction
        """
```

### 3.3 parser/relation_detector.py

功能：检测步骤间的逻辑关系

```python
class RelationType(Enum):
    SUPPORTS    = "supports"     # A支持B
    CONTRADICTS = "contradicts"  # A否定B（触发回溯）
    EXTENDS     = "extends"      # A在B基础上延伸
    BACKTRACKS  = "backtracks"   # A回溯到B
    CONCLUDES   = "concludes"    # A是B的结论

@dataclass
class StepRelation:
    source_id: int
    target_id: int
    relation_type: RelationType
    weight: float  # 0-1

class RelationDetector:
    def detect(self, steps: List[ReasoningStep]) -> List[StepRelation]:
        """
        检测策略：
        1. 默认相邻步骤之间有 EXTENDS 关系
        2. backtrack类型步骤向前搜索最近的 hypothesis 步骤，
           建立 BACKTRACKS 关系
        3. conclusion类型步骤与所有 hypothesis/deduction 建立
           CONCLUDES 关系（取最近5个）
        4. 内容相似度 > 0.7 的非相邻步骤建立 SUPPORTS 关系
           （使用 difflib.SequenceMatcher）
        """
```

### 3.4 graph/models.py

```python
@dataclass
class ReasoningGraph:
    question: str
    model_name: str
    raw_trace: str
    steps: List[ReasoningStep]
    relations: List[StepRelation]
    graph: nx.DiGraph  # networkx有向图
    metadata: dict     # 时间戳、token数等

@dataclass
class AnalysisResult:
    graph: ReasoningGraph
    metrics: dict          # 质量指标
    summary: str           # 文字摘要
```

### 3.5 graph/builder.py

```python
class GraphBuilder:
    def build(self,
              steps: List[ReasoningStep],
              relations: List[StepRelation]) -> nx.DiGraph:
        """
        节点属性：
            - step_id, content, step_type, confidence
            - color: 按step_type映射颜色
              hypothesis=蓝, deduction=绿,
              backtrack=红, verification=橙, conclusion=紫

        边属性：
            - relation_type, weight
            - style: backtrack边用虚线，其余实线
        """
```

### 3.6 graph/analyzer.py

```python
class GraphAnalyzer:
    def analyze(self, G: nx.DiGraph) -> dict:
        """
        返回以下字段：
        {
            "node_count": int,           # 推理步骤总数
            "edge_count": int,           # 关系总数
            "backtrack_count": int,      # 回溯次数
            "backtrack_ratio": float,    # 回溯步骤占比
            "max_depth": int,            # 推理链最大深度
            "branch_factor": float,      # 平均分支因子
            "critical_path": List[int],  # 关键推理路径(step_id列表)
            "has_cycle": bool,           # 是否存在循环推理
            "redundancy_score": float,   # 冗余度(0-1)
            "conclusion_steps": List[int]
        }
        冗余度计算：
            重复或高度相似内容的步骤数 / 总步骤数
            相似度阈值：0.6（difflib）
        """
```

### 3.7 metrics/quality_scorer.py

```python
class QualityScorer:
    def score(self,
              graph_metrics: dict,
              steps: List[ReasoningStep]) -> dict:
        """
        输出指标（所有分数0-100）：
        {
            "coherence_score": float,    # 连贯性
            "efficiency_score": float,   # 推理效率（越少回溯越高）
            "depth_score": float,        # 推理深度
            "confidence_score": float,   # 平均步骤置信度
            "overall_score": float,      # 加权综合分
            "grade": str,               # A/B/C/D
            "issues": List[str],         # 问题列表，自然语言
            "strengths": List[str]       # 优势列表，自然语言
        }

        评分权重：
            coherence: 30%
            efficiency: 25%
            depth: 25%
            confidence: 20%

        issues 示例：
            "检测到 3 次推理回溯，存在思路反复"
            "发现循环推理节点"
            "推理链过浅（深度仅为2）"
        """
```

### 3.8 metrics/comparator.py

```python
class ModelComparator:
    def compare(self,
                results: Dict[str, AnalysisResult]) -> dict:
        """
        输入：{model_name: AnalysisResult}
        输出：
        {
            "metric_table": pd.DataFrame,  # 各模型指标对比表
            "rankings": dict,              # 各维度排名
            "best_model": str,             # 综合最优模型
            "insights": List[str]          # 自然语言对比洞察
        }
        insights 示例：
            "DeepSeek-R1 推理效率最高，回溯次数仅为 QwQ 的 1/3"
            "QwQ-32B 推理深度最大，适合复杂多步推理任务"
        """
```

### 3.9 visualizer/graph_viz.py

```python
class GraphVisualizer:
    def to_html(self, G: nx.DiGraph, output_path: str):
        """
        使用 pyvis 生成交互式 HTML 推理树
        - 节点按 step_type 着色
        - 节点大小与 confidence 成正比
        - 边按 relation_type 着色（backtrack=红色虚线）
        - 悬停显示完整 step content
        - 支持拖拽、缩放
        """

    def to_image(self, G: nx.DiGraph, output_path: str):
        """
        使用 matplotlib 生成静态推理树图
        分层布局：使用 nx.spring_layout 或 dot 布局
        """
```

### 3.10 visualizer/report_viz.py

```python
class ReportVisualizer:
    def plot_metrics_radar(self,
                           metrics: dict,
                           output_path: str):
        """
        plotly 雷达图，展示5个维度分数
        """

    def plot_step_timeline(self,
                           steps: List[ReasoningStep],
                           output_path: str):
        """
        步骤时间线图：
        x轴=步骤序号，y轴=置信度
        颜色=step_type，标注backtrack节点
        """

    def plot_comparison_bar(self,
                            comparison: dict,
                            output_path: str):
        """
        跨模型对比条形图（plotly grouped bar）
        """
```

### 3.11 analyzer.py（统一入口）

```python
class ThinkGraphAnalyzer:
    """
    统一入口，组合所有模块
    """
    def analyze(self,
                raw_text: str,
                model_name: str = "unknown",
                question: str = "") -> AnalysisResult:
        """完整分析流程，返回 AnalysisResult"""

    def compare(self,
                inputs: Dict[str, str],
                question: str = "") -> dict:
        """
        inputs: {model_name: raw_text}
        批量分析并对比
        """

    def visualize(self,
                  result: AnalysisResult,
                  output_dir: str = "./output"):
        """
        生成所有可视化文件：
        - reasoning_tree.html（交互式）
        - reasoning_tree.png（静态）
        - metrics_radar.html
        - step_timeline.html
        """
```

---

## 4. CLI 接口要求

使用 argparse 或 click 实现：

```bash
# 分析单个文件
thinkgraph analyze --input <file> --model <name> --output <dir>

# 对比多个模型
thinkgraph compare --inputs r1.txt qwq.txt --names r1 qwq --question "问题描述"

# 从标准输入读取
cat response.txt | thinkgraph analyze --model deepseek-r1
```

在 setup.py 中注册 entry_points：
```python
entry_points={
    'console_scripts': ['thinkgraph=thinkgraph.cli:main']
}
```

---

## 5. Gradio Demo（demo/app.py）

### 布局（双栏）

**Tab 1：单模型分析**
- 左侧输入区：
  - 文本框（model name）
  - 大文本框（粘贴模型输出，含think块）
  - 按钮：Analyze
- 右侧输出区：
  - 推理树 HTML（gr.HTML）
  - 指标雷达图（gr.Plot）
  - 步骤时间线（gr.Plot）
  - 质量报告文本（grade + issues + strengths）

**Tab 2：多模型对比**
- 输入：两个模型名称 + 两个文本框 + 共同问题输入
- 输出：
  - 并排推理树（两个 gr.HTML）
  - 对比条形图（gr.Plot）
  - 洞察文字（gr.Markdown）

**示例数据：** 预置2组示例（数学推理题 + 代码调试题），
点击 "Load Example" 自动填充

---

## 6. examples/sample_r1_output.txt 要求

生成一段模拟的 DeepSeek-R1 风格输出（含 <think> 块），
要求：
- 问题：解一道数学题（如：求解方程 x² - 5x + 6 = 0）
- think块内容至少包含：假设步骤、推导步骤、一次回溯、验证步骤、结论
- 长度：400-600字

生成一段模拟的 QwQ 风格输出，同一问题，
风格差异：更多分支探索、更长的推理链

---

## 7. tests/ 要求

test_parser.py：
- test_extract_think_tags：验证标签提取
- test_segment_steps：验证至少切出3个步骤
- test_classify_backtrack：验证含"wait"的步骤被分类为backtrack

test_graph.py：
- test_build_graph：验证节点数等于步骤数
- test_analyzer_metrics：验证返回所有必要字段

test_metrics.py：
- test_scorer_output_fields：验证分数字段完整
- test_grade_assignment：验证A/B/C/D分级逻辑

---

## 8. requirements.txt

```
networkx>=3.0
pyvis>=0.3.2
matplotlib>=3.7.0
plotly>=5.15.0
gradio>=4.0.0
pandas>=2.0.0
numpy>=1.24.0
click>=8.1.0
dataclasses-json>=0.6.0
```

---

## 9. README.md 必须包含内容（按顺序）

1. 项目标题 + 一句话描述
2. 推理树可视化截图（占位：`![demo](assets/demo.png)`）
3. Features 列表（5条）
4. Installation（pip install）
5. Quick Start（10行以内代码示例）
6. 模块架构图（mermaid流程图）
7. Metrics 说明表格
8. 跨模型对比示例截图占位
9. Roadmap（3条未来计划）
10. License：MIT

---

## 10. 构建顺序（agent 执行顺序）

1. 建立目录结构 + 所有空文件
2. 实现 graph/models.py（数据结构先定义）
3. 实现 parser/ 三个文件
4. 实现 graph/builder.py 和 graph/analyzer.py
5. 实现 metrics/ 两个文件
6. 实现 visualizer/ 两个文件
7. 实现 analyzer.py（统一入口）
8. 生成 examples/ 示例数据
9. 实现 demo/app.py
10. 实现 tests/
11. 写 setup.py 和 requirements.txt
12. 写 README.md