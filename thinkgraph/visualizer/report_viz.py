"""Generate metric report visualizations (radar, timeline, comparison bar)."""

from __future__ import annotations

import os

import plotly.graph_objects as go

from thinkgraph.graph.models import ReasoningStep

_TYPE_COLOR = {
    "hypothesis": "#4A90D9",
    "deduction": "#27AE60",
    "backtrack": "#E74C3C",
    "verification": "#F39C12",
    "conclusion": "#8E44AD",
}


class ReportVisualizer:
    def plot_metrics_radar(self, metrics: dict, output_path: str) -> str:
        """5-dimension radar chart for quality metrics."""
        categories = [
            "Coherence", "Efficiency", "Depth", "Confidence", "Overall"
        ]
        values = [
            metrics.get("coherence_score", 0),
            metrics.get("efficiency_score", 0),
            metrics.get("depth_score", 0),
            metrics.get("confidence_score", 0),
            metrics.get("overall_score", 0),
        ]

        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                name="Score",
                line=dict(color="#4A90D9"),
            )
        )
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            title="Reasoning Quality Metrics",
            width=600,
            height=500,
        )
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fig.write_html(output_path)
        return output_path

    def plot_step_timeline(
        self, steps: list[ReasoningStep], output_path: str
    ) -> str:
        """Step timeline: x=step index, y=confidence, color=step_type."""
        if not steps:
            return output_path

        fig = go.Figure()
        x_vals = [s.step_id for s in steps]
        y_vals = [s.confidence * 100 for s in steps]
        colors = [_TYPE_COLOR.get(s.step_type, "#95A5A6") for s in steps]
        labels = [
            f"Step {s.step_id} [{s.step_type}]<br>{s.content[:80]}..."
            for s in steps
        ]

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines+markers+text",
                marker=dict(color=colors, size=12),
                line=dict(color="#BDC3C7"),
                text=[s.step_type for s in steps],
                textposition="top center",
                hovertext=labels,
                hoverinfo="text",
            )
        )

        # Annotate backtrack nodes
        for s in steps:
            if s.step_type == "backtrack":
                fig.add_annotation(
                    x=s.step_id,
                    y=s.confidence * 100,
                    text="↩ backtrack",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="#E74C3C",
                    font=dict(color="#E74C3C", size=10),
                )

        fig.update_layout(
            title="Reasoning Step Timeline",
            xaxis_title="Step Index",
            yaxis_title="Confidence (%)",
            width=900,
            height=450,
        )
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fig.write_html(output_path)
        return output_path

    def plot_comparison_bar(self, comparison: dict, output_path: str) -> str:
        """Grouped bar chart for cross-model comparison."""
        df = comparison.get("metric_table")
        if df is None or df.empty:
            return output_path

        score_cols = [
            c for c in ["coherence_score", "efficiency_score", "depth_score",
                         "confidence_score", "overall_score"]
            if c in df.columns
        ]
        if not score_cols:
            return output_path

        fig = go.Figure()
        for col in score_cols:
            fig.add_trace(
                go.Bar(
                    x=df.index.tolist(),
                    y=df[col].tolist(),
                    name=col.replace("_score", "").title(),
                )
            )

        fig.update_layout(
            barmode="group",
            title="Cross-Model Comparison",
            yaxis_title="Score",
            xaxis_title="Model",
            width=800,
            height=500,
        )
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fig.write_html(output_path)
        return output_path
