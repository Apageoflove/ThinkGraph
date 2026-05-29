"""Tests for graph modules."""

import pytest
import networkx as nx

from thinkgraph.graph.builder import GraphBuilder
from thinkgraph.graph.analyzer import GraphAnalyzer
from thinkgraph.graph.models import ReasoningStep, StepRelation, RelationType


def _make_steps():
    return [
        ReasoningStep(step_id=0, content="假设 x=2", step_type="hypothesis", confidence=0.7),
        ReasoningStep(step_id=1, content="推导计算过程", step_type="deduction", confidence=0.8),
        ReasoningStep(step_id=2, content="Wait 重新考虑", step_type="backtrack", confidence=0.3),
        ReasoningStep(step_id=3, content="验证结果正确", step_type="verification", confidence=0.9),
        ReasoningStep(step_id=4, content="因此结论是", step_type="conclusion", confidence=0.9),
    ]


def _make_relations(steps):
    return [
        StepRelation(source_id=0, target_id=1, relation_type=RelationType.EXTENDS),
        StepRelation(source_id=1, target_id=2, relation_type=RelationType.EXTENDS),
        StepRelation(source_id=2, target_id=0, relation_type=RelationType.BACKTRACKS, weight=0.8),
        StepRelation(source_id=2, target_id=3, relation_type=RelationType.EXTENDS),
        StepRelation(source_id=3, target_id=4, relation_type=RelationType.EXTENDS),
        StepRelation(source_id=4, target_id=1, relation_type=RelationType.CONCLUDES),
    ]


class TestGraphBuilder:
    def test_build_graph(self):
        steps = _make_steps()
        rels = _make_relations(steps)
        builder = GraphBuilder()
        G = builder.build(steps, rels)

        assert G.number_of_nodes() == len(steps)
        assert G.number_of_edges() == len(rels)

    def test_node_attributes(self):
        steps = _make_steps()
        rels = _make_relations(steps)
        G = GraphBuilder().build(steps, rels)

        for node, data in G.nodes(data=True):
            assert "step_type" in data
            assert "color" in data
            assert "confidence" in data

    def test_backtrack_edge_dashed(self):
        steps = _make_steps()
        rels = _make_relations(steps)
        G = GraphBuilder().build(steps, rels)

        backtrack_edges = [
            (u, v, d) for u, v, d in G.edges(data=True)
            if d.get("relation_type") == "backtracks"
        ]
        assert len(backtrack_edges) > 0
        for _, _, d in backtrack_edges:
            assert d["style"] == "dashed"


class TestGraphAnalyzer:
    def test_analyzer_metrics(self):
        steps = _make_steps()
        rels = _make_relations(steps)
        G = GraphBuilder().build(steps, rels)
        analyzer = GraphAnalyzer()
        metrics = analyzer.analyze(G, steps)

        required_keys = [
            "node_count", "edge_count", "backtrack_count",
            "backtrack_ratio", "max_depth", "branch_factor",
            "critical_path", "has_cycle", "redundancy_score",
            "conclusion_steps",
        ]
        for key in required_keys:
            assert key in metrics, f"Missing key: {key}"

    def test_node_count(self):
        steps = _make_steps()
        rels = _make_relations(steps)
        G = GraphBuilder().build(steps, rels)
        metrics = GraphAnalyzer().analyze(G, steps)
        assert metrics["node_count"] == 5

    def test_empty_graph(self):
        G = nx.DiGraph()
        metrics = GraphAnalyzer().analyze(G, [])
        assert metrics["node_count"] == 0
        assert metrics["max_depth"] == 0
