"""Detect logical relations between reasoning steps."""

from __future__ import annotations

import difflib
from typing import List

from thinkgraph.graph.models import ReasoningStep, RelationType, StepRelation

_SIMILARITY_THRESHOLD = 0.7
_CONCLUDE_NEIGHBOR_LIMIT = 5


class RelationDetector:
    def detect(self, steps: List[ReasoningStep]) -> List[StepRelation]:
        if len(steps) < 2:
            return []

        relations: List[StepRelation] = []

        # 1. Default EXTENDS between adjacent steps
        for i in range(len(steps) - 1):
            relations.append(
                StepRelation(
                    source_id=steps[i].step_id,
                    target_id=steps[i + 1].step_id,
                    relation_type=RelationType.EXTENDS,
                    weight=0.5,
                )
            )

        # 2. BACKTRACKS: backtrack step → nearest preceding hypothesis
        for i, step in enumerate(steps):
            if step.step_type == "backtrack":
                target = self._find_nearest(steps, i, {"hypothesis", "deduction"})
                if target is not None:
                    relations.append(
                        StepRelation(
                            source_id=step.step_id,
                            target_id=steps[target].step_id,
                            relation_type=RelationType.BACKTRACKS,
                            weight=0.8,
                        )
                    )

        # 3. CONCLUDES: conclusion → recent hypothesis/deduction steps
        for i, step in enumerate(steps):
            if step.step_type == "conclusion":
                start = max(0, i - _CONCLUDE_NEIGHBOR_LIMIT)
                for j in range(start, i):
                    if steps[j].step_type in {"hypothesis", "deduction", "verification"}:
                        relations.append(
                            StepRelation(
                                source_id=step.step_id,
                                target_id=steps[j].step_id,
                                relation_type=RelationType.CONCLUDES,
                                weight=0.7,
                            )
                        )

        # 4. SUPPORTS: high similarity between non-adjacent steps
        contents = [s.content for s in steps]
        for i in range(len(steps)):
            for j in range(i + 2, len(steps)):
                ratio = difflib.SequenceMatcher(
                    None, contents[i], contents[j]
                ).ratio()
                if ratio > _SIMILARITY_THRESHOLD:
                    relations.append(
                        StepRelation(
                            source_id=steps[j].step_id,
                            target_id=steps[i].step_id,
                            relation_type=RelationType.SUPPORTS,
                            weight=round(ratio, 3),
                        )
                    )

        return relations

    @staticmethod
    def _find_nearest(
        steps: List[ReasoningStep], index: int, types: set
    ) -> int | None:
        for i in range(index - 1, -1, -1):
            if steps[i].step_type in types:
                return i
        return None
