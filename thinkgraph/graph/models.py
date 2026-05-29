from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

import networkx as nx


class RelationType(Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    EXTENDS = "extends"
    BACKTRACKS = "backtracks"
    CONCLUDES = "concludes"


@dataclass
class ReasoningStep:
    step_id: int
    content: str
    step_type: str  # hypothesis | deduction | backtrack | verification | conclusion
    confidence: float  # 0-1
    char_count: int = 0

    def __post_init__(self):
        if self.char_count == 0:
            self.char_count = len(self.content)


@dataclass
class StepRelation:
    source_id: int
    target_id: int
    relation_type: RelationType
    weight: float = 0.5


@dataclass
class ReasoningGraph:
    question: str = ""
    model_name: str = "unknown"
    raw_trace: str = ""
    steps: List[ReasoningStep] = field(default_factory=list)
    relations: List[StepRelation] = field(default_factory=list)
    graph: Optional[nx.DiGraph] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class AnalysisResult:
    graph: ReasoningGraph
    metrics: dict = field(default_factory=dict)
    summary: str = ""
