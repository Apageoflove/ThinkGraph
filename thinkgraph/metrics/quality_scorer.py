"""Compute reasoning quality scores from graph metrics and steps."""

from __future__ import annotations

from typing import List

from thinkgraph.graph.models import ReasoningStep

_WEIGHTS = {
    "coherence": 0.30,
    "efficiency": 0.25,
    "depth": 0.25,
    "confidence": 0.20,
}


class QualityScorer:
    def score(
        self,
        graph_metrics: dict,
        steps: List[ReasoningStep],
    ) -> dict:
        coherence = self._coherence(graph_metrics)
        efficiency = self._efficiency(graph_metrics)
        depth = self._depth(graph_metrics, steps)
        confidence = self._confidence(steps)

        overall = (
            _WEIGHTS["coherence"] * coherence
            + _WEIGHTS["efficiency"] * efficiency
            + _WEIGHTS["depth"] * depth
            + _WEIGHTS["confidence"] * confidence
        )

        grade = self._grade(overall)
        issues = self._issues(graph_metrics, steps)
        strengths = self._strengths(graph_metrics, steps)

        return {
            "coherence_score": round(coherence, 2),
            "efficiency_score": round(efficiency, 2),
            "depth_score": round(depth, 2),
            "confidence_score": round(confidence, 2),
            "overall_score": round(overall, 2),
            "grade": grade,
            "issues": issues,
            "strengths": strengths,
        }

    # ------------------------------------------------------------------
    @staticmethod
    def _coherence(m: dict) -> float:
        edge_count = m.get("edge_count", 0)
        node_count = m.get("node_count", 1)
        ratio = edge_count / node_count if node_count else 0
        score = min(ratio / 2.0, 1.0) * 100
        if m.get("has_cycle"):
            score -= 10
        return max(0, min(100, score))

    @staticmethod
    def _efficiency(m: dict) -> float:
        bt = m.get("backtrack_ratio", 0)
        red = m.get("redundancy_score", 0)
        score = 100 - (bt * 100 + red * 50)
        return max(0, min(100, score))

    @staticmethod
    def _depth(m: dict, steps: list) -> float:
        max_d = m.get("max_depth", 0)
        n = len(steps) or 1
        score = min(max_d / max(n * 0.5, 1), 1.0) * 100
        return max(0, min(100, score))

    @staticmethod
    def _confidence(steps: list) -> float:
        if not steps:
            return 0.0
        avg = sum(s.confidence for s in steps) / len(steps)
        return avg * 100

    @staticmethod
    def _grade(score: float) -> str:
        if score >= 85:
            return "A"
        if score >= 70:
            return "B"
        if score >= 55:
            return "C"
        return "D"

    def _issues(self, m: dict, steps: list) -> list[str]:
        issues: list[str] = []
        bt = m.get("backtrack_count", 0)
        if bt >= 3:
            issues.append(f"检测到 {bt} 次推理回溯，存在思路反复")
        if m.get("has_cycle"):
            issues.append("发现循环推理节点")
        max_d = m.get("max_depth", 0)
        if max_d <= 2:
            issues.append(f"推理链过浅（深度仅为 {max_d}）")
        red = m.get("redundancy_score", 0)
        if red > 0.3:
            issues.append(f"推理冗余度较高（{red:.0%}）")
        if not any(s.step_type == "verification" for s in steps):
            issues.append("缺少验证步骤")
        if not any(s.step_type == "conclusion" for s in steps):
            issues.append("缺少明确的结论步骤")
        return issues

    def _strengths(self, m: dict, steps: list) -> list[str]:
        strengths: list[str] = []
        if m.get("backtrack_count", 0) == 0:
            strengths.append("推理过程无回溯，思路清晰")
        if m.get("max_depth", 0) >= 5:
            strengths.append(f"推理深度较大（深度 {m['max_depth']}）")
        if any(s.step_type == "verification" for s in steps):
            strengths.append("包含验证步骤，推理严谨")
        avg_conf = sum(s.confidence for s in steps) / len(steps) if steps else 0
        if avg_conf >= 0.8:
            strengths.append("整体置信度较高")
        types = {s.step_type for s in steps}
        if len(types) >= 4:
            strengths.append("推理步骤类型丰富，涵盖假设、推导、验证、结论")
        return strengths
