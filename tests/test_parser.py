"""Tests for parser modules."""

import pytest

from thinkgraph.parser.trace_extractor import TraceExtractor
from thinkgraph.parser.step_segmenter import StepSegmenter
from thinkgraph.parser.relation_detector import RelationDetector


class TestTraceExtractor:
    def setup_method(self):
        self.ext = TraceExtractor()

    def test_extract_think_tags(self):
        text = "<thinkHello world</think"
        assert self.ext.extract(text) == "Hello world"

    def test_extract_thinking_tags(self):
        text = "<thinkingSome reasoning</thinking"
        assert self.ext.extract(text) == "Some reasoning"

    def test_extract_no_tags(self):
        text = "Just plain text without tags"
        assert self.ext.extract(text) == text

    def test_has_thinking_trace_true(self):
        assert self.ext.has_thinking_trace("<thinkabc</think")
        assert self.ext.has_thinking_trace("<thinkingabc</thinking")

    def test_has_thinking_trace_false(self):
        assert not self.ext.has_thinking_trace("no tags here")

    def test_empty_input(self):
        assert self.ext.extract("") == ""
        assert self.ext.extract("   ") == ""


class TestStepSegmenter:
    def setup_method(self):
        self.seg = StepSegmenter()

    def test_segment_steps(self):
        text = (
            "首先假设这个方程可以用因式分解法来解，我们需要找到合适的分解方式。"
            "\n\n然后我尝试用求根公式来解这个方程。"
            "\n\nWait，让我重新考虑这个问题。"
            "\n\n最后验证一下结果是否正确。"
            "\n\n因此方程的解为 x=2 和 x=3，这是最终结论。"
        )
        steps = self.seg.segment(text)
        assert len(steps) >= 3
        assert all(s.content for s in steps)

    def test_classify_backtrack(self):
        steps = self.seg.segment("Wait, let me reconsider this approach entirely from scratch.")
        assert any(s.step_type == "backtrack" for s in steps)

    def test_classify_hypothesis(self):
        steps = self.seg.segment("假设这个函数在 x=0 处有极值，我们可以通过求导来验证。")
        assert any(s.step_type == "hypothesis" for s in steps)

    def test_classify_conclusion(self):
        steps = self.seg.segment("因此最终答案是 x=3。所以这道题的结论很明确。")
        assert any(s.step_type == "conclusion" for s in steps)

    def test_empty_input(self):
        assert self.seg.segment("") == []


class TestRelationDetector:
    def setup_method(self):
        self.det = RelationDetector()
        self.seg = StepSegmenter()

    def test_detect_extends(self):
        text = (
            "首先分析问题的已知条件。"
            "\n\n然后根据已知条件进行推导运算。"
            "\n\n最后得出最终答案。"
        )
        steps = self.seg.segment(text)
        rels = self.det.detect(steps)
        types = {r.relation_type.value for r in rels}
        assert "extends" in types

    def test_detect_with_backtrack(self):
        text = (
            "假设答案是 x=2。"
            "\n\n让我进行一些推导计算。"
            "\n\nWait，让我重新考虑假设是否成立。"
            "\n\n因此最终结论是正确的。"
        )
        steps = self.seg.segment(text)
        rels = self.det.detect(steps)
        types = {r.relation_type.value for r in rels}
        assert "backtracks" in types or "extends" in types
