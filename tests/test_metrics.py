"""Tests for metrics modules."""

import pytest

from thinkgraph.graph.models import ReasoningStep
from thinkgraph.metrics.quality_scorer import QualityScorer


def _make_graph_metrics(overrides=None):
    base = {
        "node_count": 6,
        "edge_count": 8,
        "backtrack_count": 1,
        "backtrack_ratio": 0.16,
        "max_depth": 4,
        "branch_factor": 1.33,
        "critical_path": [0, 1, 2, 3, 4],
        "has_cycle": False,
        "redundancy_score": 0.1,
        "conclusion_steps": [5],
    }
    if overrides:
        base.update(overrides)
    return base


def _make_steps():
    return [
        ReasoningStep(step_id=0, content="假设 x=2", step_type="hypothesis", confidence=0.7),
        ReasoningStep(step_id=1, content="推导第一步", step_type="deduction", confidence=0.8),
        ReasoningStep(step_id=2, content="推导第二步", step_type="deduction", confidence=0.75),
        ReasoningStep(step_id=3, content="Wait 重新考虑", step_type="backtrack", confidence=0.3),
        ReasoningStep(step_id=4, content="验证结果", step_type="verification", confidence=0.9),
        ReasoningStep(step_id=5, content="因此结论是", step_type="conclusion", confidence=0.9),
    ]


class TestQualityScorer:
    def setup_method(self):
        self.scorer = QualityScorer()

    def test_scorer_output_fields(self):
        metrics = self.scorer.score(_make_graph_metrics(), _make_steps())
        required = [
            "coherence_score", "efficiency_score", "depth_score",
            "confidence_score", "overall_score", "grade",
            "issues", "strengths",
        ]
        for key in required:
            assert key in metrics, f"Missing: {key}"

    def test_score_ranges(self):
        metrics = self.scorer.score(_make_graph_metrics(), _make_steps())
        for key in ["coherence_score", "efficiency_score", "depth_score",
                     "confidence_score", "overall_score"]:
            assert 0 <= metrics[key] <= 100, f"{key} out of range: {metrics[key]}"

    def test_grade_assignment(self):
        # High scores should give A or B
        good_metrics = _make_graph_metrics({
            "backtrack_count": 0,
            "backtrack_ratio": 0.0,
            "has_cycle": False,
            "redundancy_score": 0.0,
            "max_depth": 5,
            "edge_count": 12,
        })
        result = self.scorer.score(good_metrics, _make_steps())
        assert result["grade"] in {"A", "B", "C", "D"}

    def test_low_grade(self):
        bad_metrics = _make_graph_metrics({
            "backtrack_count": 5,
            "backtrack_ratio": 0.5,
            "has_cycle": True,
            "redundancy_score": 0.6,
            "max_depth": 1,
            "edge_count": 2,
        })
        steps = [ReasoningStep(step_id=i, content=f"step {i}", step_type="deduction", confidence=0.3) for i in range(6)]
        result = self.scorer.score(bad_metrics, steps)
        assert result["grade"] in {"C", "D"}

    def test_issues_generated(self):
        bad_metrics = _make_graph_metrics({
            "backtrack_count": 4,
            "has_cycle": True,
        })
        result = self.scorer.score(bad_metrics, _make_steps())
        assert len(result["issues"]) > 0

    def test_strengths_generated(self):
        result = self.scorer.score(_make_graph_metrics(), _make_steps())
        assert len(result["strengths"]) > 0
