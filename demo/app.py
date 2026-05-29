"""Gradio Demo for ThinkGraph."""

from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import gradio as gr

from thinkgraph.analyzer import ThinkGraphAnalyzer

analyzer = ThinkGraphAnalyzer()

_SAMPLE_R1 = """<think首先，我需要解方程 x² - 5x + 6 = 0。

我可以尝试使用因式分解法。假设 x² - 5x + 6 可以分解为 (x - a)(x - b) 的形式，其中 a + b = 5，ab = 6。

让我找出满足条件的 a 和 b。6 的因数对有 (1, 6) 和 (2, 3)。其中 2 + 3 = 5，满足条件。因此可以分解为 (x - 2)(x - 3) = 0。

Wait, 让我验证一下这个分解是否正确。展开 (x - 2)(x - 3) = x² - 3x - 2x + 6 = x² - 5x + 6。确认无误。

因此方程 (x - 2)(x - 3) = 0 的解为 x = 2 或 x = 3。

我再用求根公式验证一次。对于 ax² + bx + c = 0，判别式 Δ = b² - 4ac = 25 - 24 = 1 > 0，所以有两个不同的实根。

x = (5 ± 1) / 2，即 x₁ = 3，x₂ = 2。与因式分解结果一致。

综上，方程 x² - 5x + 6 = 0 的解为 x = 2 和 x = 3。</think"""

_SAMPLE_QWQ = """<think我需要解方程 x² - 5x + 6 = 0。让我从多个角度来分析这个问题。

首先假设这个方程可以用因式分解法来解。我需要找到两个数 a 和 b，使得 a + b = 5 且 ab = 6。

6 的所有因数对包括 (1, 6)、(2, 3)、(-1, -6)、(-2, -3)。正数对中，2 + 3 = 5，正好满足条件。所以可以写成 (x - 2)(x - 3) = 0。

不过让我也考虑一下求根公式的方法。对于一般形式 ax² + bx + c = 0，判别式 Δ = b² - 4ac = (-5)² - 4×1×6 = 25 - 24 = 1。

因为 Δ > 0，所以方程有两个不相等的实数根。

Wait，我再想想，有没有可能有复数解？不对，Δ = 1 > 0，所以一定是两个实根，不需要考虑复数。

用求根公式：x = (5 ± √1) / 2 = (5 ± 1) / 2
x₁ = (5 + 1) / 2 = 3
x₂ = (5 - 1) / 2 = 2

让我验证 x₁ = 3：3² - 5×3 + 6 = 9 - 15 + 6 = 0 ✓
验证 x₂ = 2：2² - 5×2 + 6 = 4 - 10 + 6 = 0 ✓

两个解都验证通过。我还想检查一下是否可以用配方法：x² - 5x + 6 = (x - 5/2)² - 25/4 + 6 = (x - 5/2)² - 1/4 = 0，所以 (x - 5/2)² = 1/4，x - 5/2 = ±1/2，x = 3 或 x = 2。结果一致。

综合以上三种方法（因式分解、求根公式、配方法），都得到相同的结论：方程 x² - 5x + 6 = 0 的解为 x = 2 和 x = 3。</think"""


def run_analysis(model_name: str, raw_text: str):
    if not raw_text.strip():
        return None, None, None, "Please paste model output text."
    result = analyzer.analyze(raw_text, model_name=model_name or "unknown")

    tmpdir = tempfile.mkdtemp()
    html_path = os.path.join(tmpdir, "tree.html")
    radar_path = os.path.join(tmpdir, "radar.html")
    timeline_path = os.path.join(tmpdir, "timeline.html")

    if result.graph.graph and result.graph.graph.number_of_nodes() > 0:
        analyzer.graph_viz.to_html(result.graph.graph, html_path)
        tree_html = open(html_path, "r", encoding="utf-8").read() if os.path.exists(html_path) else "<p>No graph</p>"
    else:
        tree_html = "<p>No reasoning steps detected.</p>"

    analyzer.report_viz.plot_metrics_radar(result.metrics, radar_path)
    radar_fig = _load_plotly_html(radar_path)

    analyzer.report_viz.plot_step_timeline(result.graph.steps, timeline_path)
    timeline_fig = _load_plotly_html(timeline_path)

    report_md = _format_report(result)
    return tree_html, radar_fig, timeline_fig, report_md


def run_comparison(
    model_a_name: str, text_a: str,
    model_b_name: str, text_b: str,
    question: str,
):
    if not text_a.strip() or not text_b.strip():
        return None, None, "Please provide both model outputs."

    inputs = {
        model_a_name or "Model A": text_a,
        model_b_name or "Model B": text_b,
    }
    comp = analyzer.compare(inputs, question=question)

    tmpdir = tempfile.mkdtemp()
    bar_path = os.path.join(tmpdir, "comparison.html")
    analyzer.report_viz.plot_comparison_bar(comp, bar_path)
    bar_fig = _load_plotly_html(bar_path)

    # Generate side-by-side tree HTML
    tree_htmls = []
    for name, text in inputs.items():
        result = analyzer.analyze(text, model_name=name, question=question)
        tp = os.path.join(tmpdir, f"tree_{name}.html")
        if result.graph.graph and result.graph.graph.number_of_nodes() > 0:
            analyzer.graph_viz.to_html(result.graph.graph, tp)
            h = open(tp, "r", encoding="utf-8").read() if os.path.exists(tp) else ""
            tree_htmls.append(h)

    combined = "<div style='display:flex;gap:10px;'>"
    for h in tree_htmls:
        combined += f"<div style='flex:1;min-width:0;'>{h}</div>"
    combined += "</div>"

    insights_md = "## Comparison Insights\n\n"
    insights_md += f"**Best Model:** {comp['best_model']}\n\n"
    for ins in comp["insights"]:
        insights_md += f"- {ins}\n"

    return combined, bar_fig, insights_md


def _load_plotly_html(path: str):
    """Load a Plotly HTML file and return as gr.Plot-compatible figure."""
    if not os.path.exists(path):
        return None
    import json
    import re
    content = open(path, "r", encoding="utf-8").read()
    # Extract Plotly data from the saved HTML
    match = re.search(r'Plotly\.newPlot\([^,]+,\s*(\{.*?\}),\s*\{', content, re.DOTALL)
    if match:
        try:
            fig_data = json.loads(match.group(1))
            import plotly.io as pio
            return pio.from_json(json.dumps(fig_data))
        except Exception:
            pass
    # Fallback: re-create from the data
    return None


def _format_report(result):
    m = result.metrics
    lines = [
        f"## Quality Report — {result.graph.model_name}",
        f"**Grade:** {m.get('grade', '-')}  |  **Overall Score:** {m.get('overall_score', 0):.1f}/100",
        "",
        f"| Dimension | Score |",
        f"|-----------|-------|",
        f"| Coherence | {m.get('coherence_score', 0):.1f} |",
        f"| Efficiency | {m.get('efficiency_score', 0):.1f} |",
        f"| Depth | {m.get('depth_score', 0):.1f} |",
        f"| Confidence | {m.get('confidence_score', 0):.1f} |",
        "",
    ]
    issues = m.get("issues", [])
    if issues:
        lines.append("### Issues")
        for i in issues:
            lines.append(f"- {i}")
        lines.append("")
    strengths = m.get("strengths", [])
    if strengths:
        lines.append("### Strengths")
        for s in strengths:
            lines.append(f"- {s}")
    return "\n".join(lines)


# ======================== Gradio UI ========================

with gr.Blocks(
    title="ThinkGraph Demo",
    theme=gr.themes.Soft(),
) as demo:
    gr.Markdown("# ThinkGraph — Reasoning Trace Analyzer")
    gr.Markdown("Paste a thinking model's output and analyze its reasoning structure.")

    with gr.Tabs():
        with gr.Tab("Single Model Analysis"):
            with gr.Row():
                with gr.Column(scale=1):
                    model_input = gr.Textbox(label="Model Name", value="deepseek-r1")
                    text_input = gr.Textbox(
                        label="Model Output (with <think...> tags)",
                        lines=15,
                        placeholder="Paste model output here...",
                    )
                    analyze_btn = gr.Button("Analyze", variant="primary")
                    load_ex_btn = gr.Button("Load Example")

                with gr.Column(scale=2):
                    tree_output = gr.HTML(label="Reasoning Tree")
                    with gr.Row():
                        radar_output = gr.Plot(label="Metrics Radar")
                        timeline_output = gr.Plot(label="Step Timeline")
                    report_output = gr.Markdown(label="Quality Report")

            analyze_btn.click(
                run_analysis,
                inputs=[model_input, text_input],
                outputs=[tree_output, radar_output, timeline_output, report_output],
            )
            load_ex_btn.click(
                lambda: ("deepseek-r1", _SAMPLE_R1),
                outputs=[model_input, text_input],
            )

        with gr.Tab("Model Comparison"):
            with gr.Row():
                with gr.Column():
                    a_name = gr.Textbox(label="Model A Name", value="DeepSeek-R1")
                    a_text = gr.Textbox(label="Model A Output", lines=10)
                with gr.Column():
                    b_name = gr.Textbox(label="Model B Name", value="QwQ-32B")
                    b_text = gr.Textbox(label="Model B Output", lines=10)
            question_input = gr.Textbox(label="Shared Question (optional)")
            compare_btn = gr.Button("Compare", variant="primary")
            load_comp_btn = gr.Button("Load Example Pair")
            comp_trees = gr.HTML(label="Side-by-Side Reasoning Trees")
            comp_bar = gr.Plot(label="Comparison Chart")
            comp_insights = gr.Markdown(label="Insights")

            compare_btn.click(
                run_comparison,
                inputs=[a_name, a_text, b_name, b_text, question_input],
                outputs=[comp_trees, comp_bar, comp_insights],
            )
            load_comp_btn.click(
                lambda: ("DeepSeek-R1", _SAMPLE_R1, "QwQ-32B", _SAMPLE_QWQ, "求解方程 x² - 5x + 6 = 0"),
                outputs=[a_name, a_text, b_name, b_text, question_input],
            )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
