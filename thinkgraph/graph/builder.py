"""Build a networkx DiGraph from reasoning steps and relations."""

from __future__ import annotations

import networkx as nx

from thinkgraph.graph.models import RelationType, ReasoningStep, StepRelation

_TYPE_COLOR = {
    "hypothesis": "#4A90D9",
    "deduction": "#27AE60",
    "backtrack": "#E74C3C",
    "verification": "#F39C12",
    "conclusion": "#8E44AD",
}


class GraphBuilder:
    def build(
        self,
        steps: list[ReasoningStep],
        relations: list[StepRelation],
    ) -> nx.DiGraph:
        G = nx.DiGraph()

        for step in steps:
            G.add_node(
                step.step_id,
                step_id=step.step_id,
                content=step.content,
                step_type=step.step_type,
                confidence=step.confidence,
                color=_TYPE_COLOR.get(step.step_type, "#95A5A6"),
            )

        for rel in relations:
            style = "dashed" if rel.relation_type == RelationType.BACKTRACKS else "solid"
            edge_color = "#E74C3C" if rel.relation_type == RelationType.BACKTRACKS else "#BDC3C7"
            G.add_edge(
                rel.source_id,
                rel.target_id,
                relation_type=rel.relation_type.value,
                weight=rel.weight,
                style=style,
                color=edge_color,
            )

        return G
