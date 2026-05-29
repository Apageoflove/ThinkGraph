"""Extract thinking trace content from raw model output text."""

from __future__ import annotations

import re


class TraceExtractor:
    _THINK_PATTERN = re.compile(
        r"<think(?!ing)(?:[^>]*>)?(.*?)(?:</think(?!ing)\s*>|</think(?!ing))",
        re.DOTALL,
    )
    _THINKING_PATTERN = re.compile(
        r"<thinking(?:[^>]*>)?(.*?)(?:</thinking\s*>|</thinking)",
        re.DOTALL,
    )

    def extract(self, raw_text: str) -> str:
        stripped = raw_text.strip()
        if not stripped:
            return ""

        m = self._THINK_PATTERN.search(stripped)
        if m:
            return m.group(1).strip()

        m = self._THINKING_PATTERN.search(stripped)
        if m:
            return m.group(1).strip()

        return stripped

    def has_thinking_trace(self, raw_text: str) -> bool:
        return bool(
            self._THINK_PATTERN.search(raw_text)
            or self._THINKING_PATTERN.search(raw_text)
        )
