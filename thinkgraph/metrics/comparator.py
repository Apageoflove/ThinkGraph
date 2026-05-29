"""Compare analysis results across models."""

from __future__ import annotations

from typing import Dict

import pandas as pd

from thinkgraph.graph.models import AnalysisResult


class ModelComparator:
    def compare(
        self,
        results: Dict[str, AnalysisResult],
    ) -> dict:
        if not results:
            return {
                "metric_table": pd.DataFrame(),
                "rankings": {},
                "best_model": "",
                "insights": [],
            }

        metric_keys = [
            "coherence_score",
            "efficiency_score",
            "depth_score",
            "confidence_score",
            "overall_score",
        ]

        rows = {}
        for name, result in results.items():
            rows[name] = {k: result.metrics.get(k, 0) for k in metric_keys}
            gm = result.graph.metadata.get("graph_metrics", {})
            rows[name]["backtrack_count"] = gm.get("backtrack_count", 0)
            rows[name]["step_count"] = gm.get("node_count", 0)

        df = pd.DataFrame(rows).T
        df.index.name = "model"

        rankings = {}
        for col in metric_keys:
            if col in df.columns:
                rankings[col] = df[col].sort_values(ascending=False).index.tolist()

        best_model = df["overall_score"].idxmax() if "overall_score" in df.columns else ""

        insights = self._generate_insights(df, results)

        return {
            "metric_table": df,
            "rankings": rankings,
            "best_model": best_model,
            "insights": insights,
        }

    # ------------------------------------------------------------------
    def _generate_insights(
        self, df: pd.DataFrame, results: dict
    ) -> list[str]:
        insights: list[str] = []
        models = list(results.keys())
        if len(models) < 2:
            return insights

        if "overall_score" in df.columns:
            best = df["overall_score"].idxmax()
            worst = df["overall_score"].idxmin()
            diff = df["overall_score"].max() - df["overall_score"].min()
            insights.append(
                f"{best} 综合得分最高，超出 {worst} {diff:.1f} 分"
            )

        if "efficiency_score" in df.columns:
            best_eff = df["efficiency_score"].idxmax()
            insights.append(f"{best_eff} 推理效率最高")

        if "backtrack_count" in df.columns:
            min_bt_model = df["backtrack_count"].idxmin()
            min_bt = df["backtrack_count"].min()
            insights.append(f"{min_bt_model} 回溯次数最少（{min_bt} 次）")

        if "depth_score" in df.columns:
            best_depth = df["depth_score"].idxmax()
            insights.append(f"{best_depth} 推理深度最大，适合复杂多步推理任务")

        return insights
