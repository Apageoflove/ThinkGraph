"""Segment reasoning trace text into semantic steps."""

from __future__ import annotations

import re
from typing import List

from thinkgraph.graph.models import ReasoningStep

_MIN_STEP_LEN = 10
_MAX_STEP_LEN = 500

# (?!\d) keeps decimals like 1.4142 from being read as the list marker "1."
_EXPLICIT_NUM = re.compile(
    r"(?:^|\n)\s*(?:Step\s*\d+[:.]\s*|\d+[.)](?!\d)\s*)", re.IGNORECASE
)
_PARAGRAPH_SPLIT = re.compile(r"\n{2,}")

_BACKTRACK_KW = re.compile(
    r"(?:wait|actually|no,|let me reconsider|不对|重新|让我重新|backtrack|回溯)",
    re.IGNORECASE,
)
_HYPOTHESIS_KW = re.compile(
    r"(?:assume|suppose|if\s|假设|如果|猜测|猜想|let's say)",
    re.IGNORECASE,
)
_CONCLUSION_KW = re.compile(
    r"(?:therefore|so\s|thus|hence|因此|所以|综上|总而言之|结论是|最终|in conclusion)",
    re.IGNORECASE,
)
_VERIFICATION_KW = re.compile(
    r"(?:check|verify|验证|检查|确认|核实|let me verify|double.check)",
    re.IGNORECASE,
)

_CONFIDENCE_HIGH = re.compile(
    r"(?:certain|definitely|sure|肯定|确定|一定|clearly|obviously)",
    re.IGNORECASE,
)
_CONFIDENCE_LOW = re.compile(
    r"(?:maybe|perhaps|might|可能|大概|也许|不确定|uncertain|not sure)",
    re.IGNORECASE,
)


class StepSegmenter:
    def segment(self, trace_text: str) -> List[ReasoningStep]:
        if not trace_text.strip():
            return []

        raw_chunks = self._split(trace_text)
        steps: List[ReasoningStep] = []
        for i, chunk in enumerate(raw_chunks):
            chunk = chunk.strip()
            if not chunk:
                continue
            step_type = self._classify_step_type(chunk)
            confidence = self._estimate_confidence(chunk, step_type)
            steps.append(
                ReasoningStep(
                    step_id=i,
                    content=chunk,
                    step_type=step_type,
                    confidence=confidence,
                )
            )
        return steps

    def _split(self, text: str) -> List[str]:
        # 1. Explicit numbered splits
        parts = _EXPLICIT_NUM.split(text)
        if len(parts) >= 3:
            return self._normalize(parts)

        # 2. Paragraph boundaries (most reliable)
        parts = _PARAGRAPH_SPLIT.split(text)
        if len(parts) >= 2:
            return self._normalize(parts)

        # 3. Sentence-level split for long single-paragraph text
        if len(text) > _MAX_STEP_LEN:
            parts = re.split(r"(?<=[。！？\.!?])\s*", text)
            return self._normalize(parts)

        # 4. Whole text as one step
        return [text.strip()]

    def _normalize(self, chunks: List[str]) -> List[str]:
        result: List[str] = []
        for c in chunks:
            c = c.strip()
            if not c:
                continue
            if result and len(c) < _MIN_STEP_LEN:
                result[-1] += " " + c
            else:
                result.append(c)
        return result

    def _classify_step_type(self, text: str) -> str:
        if _BACKTRACK_KW.search(text):
            return "backtrack"
        if _HYPOTHESIS_KW.search(text):
            return "hypothesis"
        if _CONCLUSION_KW.search(text):
            return "conclusion"
        if _VERIFICATION_KW.search(text):
            return "verification"
        return "deduction"

    def _estimate_confidence(self, text: str, step_type: str) -> float:
        if step_type == "backtrack":
            return 0.3
        if step_type == "conclusion":
            return 0.9
        if _CONFIDENCE_HIGH.search(text):
            return 0.85
        if _CONFIDENCE_LOW.search(text):
            return 0.5
        return 0.7
