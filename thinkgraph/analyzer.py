"""ThinkGraph unified entry point."""

from __future__ import annotations

import os
import time
from typing import Dict

from thinkgraph.graph.models import AnalysisResult, ReasoningGraph
from thinkgraph.graph.builder import GraphBuilder
from thinkgraph.graph.analyzer import GraphAnalyzer
from thinkgraph.parser.trace_extractor import TraceExtractor
from thinkgraph.parser.step_segmenter import StepSegmenter
from thinkgraph.parser.relation_detector import RelationDetector
from thinkgraph.metrics.quality_scorer import QualityScorer
from thinkgraph.metrics.comparator import ModelComparator
from thinkgraph.visualizer.graph_viz import GraphVisualizer
from thinkgraph.visualizer.report_viz import ReportVisualizer


class ThinkGraphAnalyzer:
    def __init__(self):
        self.extractor = TraceExtractor()
        self.segmenter = StepSegmenter()
        self.relation_detector = RelationDetector()
        self.graph_builder = GraphBuilder()
        self.graph_analyzer = GraphAnalyzer()
        self.scorer = QualityScorer()
        self.comparator = ModelComparator()
        self.graph_viz = GraphVisualizer()
        self.report_viz = ReportVisualizer()

    def analyze(
        self,
        raw_text: str,
        model_name: str = "unknown",
        question: str = "",
    ) -> AnalysisResult:
        trace = self.extractor.extract(raw_text)
        steps = self.segmenter.segment(trace)
        relations = self.relation_detector.detect(steps)
        G = self.graph_builder.build(steps, relations)
        graph_metrics = self.graph_analyzer.analyze(G, steps)
        metrics = self.scorer.score(graph_metrics, steps)

        rgraph = ReasoningGraph(
            question=question,
            model_name=model_name,
            raw_trace=trace,
            steps=steps,
            relations=relations,
            graph=G,
            metadata={
                "graph_metrics": graph_metrics,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "trace_length": len(trace),
                "step_count": len(steps),
            },
        )

        summary = self._build_summary(rgraph, metrics)
        return AnalysisResult(graph=rgraph, metrics=metrics, summary=summary)

    def compare(
        self,
        inputs: Dict[str, str],
        question: str = "",
    ) -> dict:
        results: Dict[str, AnalysisResult] = {}
        for name, text in inputs.items():
            results[name] = self.analyze(text, model_name=name, question=question)
        return self.comparator.compare(results)

    def visualize(
        self,
        result: AnalysisResult,
        output_dir: str = "./output",
    ) -> dict:
        os.makedirs(output_dir, exist_ok=True)
        model = result.graph.model_name or "model"
        prefix = os.path.join(output_dir, model)

        paths = {}
        if result.graph.graph is not None and result.graph.graph.number_of_nodes() > 0:
            paths["html_tree"] = self.graph_viz.to_html(
                result.graph.graph, f"{prefix}_reasoning_tree.html"
            )
            paths["image_tree"] = self.graph_viz.to_image(
                result.graph.graph, f"{prefix}_reasoning_tree.png"
            )
        paths["radar"] = self.report_viz.plot_metrics_radar(
            result.metrics, f"{prefix}_metrics_radar.html"
        )
        if result.graph.steps:
            paths["timeline"] = self.report_viz.plot_step_timeline(
                result.graph.steps, f"{prefix}_step_timeline.html"
            )
        return paths

    # ------------------------------------------------------------------
    @staticmethod
    def _build_summary(graph: ReasoningGraph, metrics: dict) -> str:
        lines = [
            f"模型: {graph.model_name}",
            f"推理步骤数: {len(graph.steps)}",
            f"综合评分: {metrics.get('overall_score', 0):.1f} ({metrics.get('grade', '-')})",
        ]
        issues = metrics.get("issues", [])
        if issues:
            lines.append("问题:")
            for i in issues:
                lines.append(f"  - {i}")
        strengths = metrics.get("strengths", [])
        if strengths:
            lines.append("优势:")
            for s in strengths:
                lines.append(f"  + {s}")
        return "\n".join(lines)
