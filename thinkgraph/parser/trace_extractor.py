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
    # Openers used when the closing tag never arrives (output truncated by
    # max_tokens mid-reasoning). Anchored to the start of the text so tags
    # mentioned inside the body are not touched.
    _THINK_OPEN = re.compile(r"<think(?!ing)[^>]*>")
    _THINKING_OPEN = re.compile(r"<thinking[^>]*>")

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

        open_m = self._THINK_OPEN.match(stripped) or self._THINKING_OPEN.match(
            stripped
        )
        if open_m:
            return stripped[open_m.end():].strip()

        return stripped

    def has_thinking_trace(self, raw_text: str) -> bool:
        return bool(
            self._THINK_PATTERN.search(raw_text)
            or self._THINKING_PATTERN.search(raw_text)
        )
