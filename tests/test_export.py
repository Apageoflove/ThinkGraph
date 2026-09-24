"""Tests for thinkgraph.visualizer.export (DOT / Mermaid / JSON)."""

from __future__ import annotations

import json

import networkx as nx
import pytest

from thinkgraph.visualizer.export import to_dot, to_json, to_mermaid


@pytest.fixture()
def graph():
    """A small graph that mirrors builder.py's node/edge attributes."""
    G = nx.DiGraph()
    G.add_node(
        0,
        step_id=0,
        step_type="hypothesis",
        confidence=0.8,
        content='Assume "x > 0" [holds] | always',
    )
    G.add_node(
        1,
        step_id=1,
        step_type="backtrack",
        confidence=0.3,
        content="Wait,\nreconsider\nthe `assumption` {entirely}",
    )
    G.add_node(2, step_id=2, step_type="conclusion", confidence=0.9, content="Done")
    G.add_edge(0, 1, relation_type="backtracks", weight=0.8, style="dashed")
    G.add_edge(1, 2, relation_type="concludes", weight=0.7, style="solid")
    return G


class TestDot:
    def test_structure(self, graph):
        dot = to_dot(graph)
        assert dot.startswith("strict digraph reasoning {")
        assert dot.rstrip().endswith("}")
        assert '"0" -> "1" [label="backtracks"];' in dot
        assert '"1" -> "2" [label="concludes"];' in dot

    def test_type_fills(self, graph):
        dot = to_dot(graph)
        assert 'fillcolor="#4A90D9"' in dot  # hypothesis
        assert 'fillcolor="#E74C3C"' in dot  # backtrack
        assert 'fillcolor="#8E44AD"' in dot  # conclusion

    def test_unsafe_chars_never_reach_labels(self, graph):
        import re

        dot = to_dot(graph)
        # Every label= value must be a single quoted run with none of the
        # characters that would terminate it early.
        labels = re.findall(r'label="([^"]*)"', dot)
        assert labels  # sanity: we actually matched some
        for inner in labels:
            for ch in '[]"|<>`\\{}':
                assert ch not in inner

    def test_writes_file(self, graph, tmp_path):
        out = tmp_path / "sub" / "g.dot"
        to_dot(graph, str(out))
        assert out.read_text(encoding="utf-8").startswith("strict digraph")


class TestMermaid:
    def test_structure(self, graph):
        mermaid = to_mermaid(graph)
        assert mermaid.startswith("flowchart TD")
        assert "n0 -->|backtracks| n1" in mermaid
        assert "n1 -->|concludes| n2" in mermaid

    def test_class_defs_only_for_present_types(self, graph):
        mermaid = to_mermaid(graph)
        assert "classDef hypothesis fill:#4A90D9" in mermaid
        assert "classDef deduction" not in mermaid  # type absent from graph

    def test_labels_are_paste_safe(self, graph):
        mermaid = to_mermaid(graph)
        for line in mermaid.splitlines():
            if line.strip().startswith("n") and '["' in line:
                inner = line.split('["')[1].split('"]')[0]
                for ch in '[]"|<>`\\{}':
                    assert ch not in inner


class TestJson:
    def test_roundtrip_preserves_raw_content(self, graph):
        payload = json.loads(to_json(graph))
        contents = {n["step_id"]: n["content"] for n in payload["nodes"]}
        assert contents[0] == 'Assume "x > 0" [holds] | always'
        assert contents[1] == "Wait,\nreconsider\nthe `assumption` {entirely}"

    def test_edges_carry_attributes(self, graph):
        payload = json.loads(to_json(graph))
        edge = next(e for e in payload["edges"] if e["source"] == 0)
        assert edge["relation_type"] == "backtracks"
        assert edge["weight"] == 0.8


class TestEmptyGraph:
    def test_all_formats_valid_on_empty(self):
        G = nx.DiGraph()
        assert to_dot(G) == "strict digraph reasoning {\n}\n"
        assert to_mermaid(G) == "flowchart TD\n"
        payload = json.loads(to_json(G))
        assert payload["nodes"] == [] and payload["edges"] == []
