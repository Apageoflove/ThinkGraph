"""Analyze reasoning graph structure and compute graph-level metrics."""

from __future__ import annotations

import difflib
from typing import List

import networkx as nx

from thinkgraph.graph.models import ReasoningStep

_REDUNDANCY_THRESHOLD = 0.6


class GraphAnalyzer:
    def analyze(self, G: nx.DiGraph, steps: List[ReasoningStep] | None = None) -> dict:
        node_count = G.number_of_nodes()
        edge_count = G.number_of_edges()

        backtrack_count = sum(
            1 for _, _, d in G.edges(data=True) if d.get("relation_type") == "backtracks"
        )
        backtrack_nodes = sum(
            1 for _, d in G.nodes(data=True) if d.get("step_type") == "backtrack"
        )
        backtrack_ratio = backtrack_nodes / node_count if node_count else 0.0

        max_depth = self._max_depth(G)
        branch_factor = self._avg_branch_factor(G)

        critical_path = self._critical_path(G)

        has_cycle = not nx.is_directed_acyclic_graph(G)

        redundancy_score = self._redundancy(steps) if steps else 0.0

        conclusion_steps = [
            n for n, d in G.nodes(data=True) if d.get("step_type") == "conclusion"
        ]

        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "backtrack_count": backtrack_count,
            "backtrack_ratio": round(backtrack_ratio, 4),
            "max_depth": max_depth,
            "branch_factor": round(branch_factor, 4),
            "critical_path": critical_path,
            "has_cycle": has_cycle,
            "redundancy_score": round(redundancy_score, 4),
            "conclusion_steps": conclusion_steps,
        }

    # ------------------------------------------------------------------
    @staticmethod
    def _max_depth(G: nx.DiGraph) -> int:
        if G.number_of_nodes() == 0:
            return 0
        try:
            return nx.dag_longest_path_length(G)
        except Exception:
            return 0

    @staticmethod
    def _avg_branch_factor(G: nx.DiGraph) -> float:
        n = G.number_of_nodes()
        if n == 0:
            return 0.0
        return G.number_of_edges() / n

    @staticmethod
    def _critical_path(G: nx.DiGraph) -> list[int]:
        if G.number_of_nodes() == 0:
            return []
        try:
            return nx.dag_longest_path(G)
        except Exception:
            return list(G.nodes())

    @staticmethod
    def _redundancy(steps: List[ReasoningStep]) -> float:
        if not steps or len(steps) < 2:
            return 0.0
        redundant = 0
        contents = [s.content for s in steps]
        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                ratio = difflib.SequenceMatcher(
                    None, contents[i], contents[j]
                ).ratio()
                if ratio > _REDUNDANCY_THRESHOLD:
                    redundant += 1
                    break
        return redundant / len(steps)
