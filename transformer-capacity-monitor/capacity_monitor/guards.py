"""Rule-based guardrails: text limits, blocked words, unsafe-instruction scan, PII filter, retries.

These are plain rules. They do not call any AI model.
"""

from __future__ import annotations

import re
import time
from typing import Callable, Iterable

MAX_TEXT_LENGTH = 2000

# Phrases that look like instructions aimed at an automated system. Feed text is data, never orders;
# anything matching is quarantined for the reviewer and never acted on.
UNSAFE_PATTERNS = [
    r"ignore (all |any |your |the )?(previous |prior |above )?(instructions|rules)",
    r"disregard (all |any |your |the )?(previous |prior )?(instructions|rules)",
    r"forward (this|it) to",
    r"system prompt",
    r"you are now",
    r"<script",
    r"javascript:",
    r"\bexec\(",
    r"\brm -rf\b",
    r"change (the )?(rating|setting|tap|breaker)",
]
BLOCKED_WORDS = ["password", "api key", "secret key", "bank account", "credit card"]

_PII_PATTERNS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[email removed]"),
    (re.compile(r"\b(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}\b"), "[phone removed]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[id removed]"),
]


def check_text(value: object, field: str, max_len: int = MAX_TEXT_LENGTH) -> list[str]:
    """Return a list of problems found in a free-text input (empty list means clean)."""
    problems: list[str] = []
    if value is None:
        return problems
    text = str(value)
    if len(text) > max_len:
        problems.append(f"{field}: text is {len(text)} characters, limit is {max_len}")
    low = text.lower()
    for pat in UNSAFE_PATTERNS:
        if re.search(pat, low):
            problems.append(f"{field}: contains instruction-like text ({pat!r}); treated as data only")
            break
    for word in BLOCKED_WORDS:
        if word in low:
            problems.append(f"{field}: contains blocked term {word!r}")
            break
    return problems


def scan_rows(rows: Iterable[dict], text_fields: Iterable[str], label: str) -> list[str]:
    """Scan selected text fields of many rows; returns problem strings with row context."""
    problems: list[str] = []
    fields = list(text_fields)
    for idx, row in enumerate(rows):
        for f in fields:
            for p in check_text(row.get(f), f"{label} row {idx + 1} {f}", max_len=500):
                problems.append(p)
    return problems


def redact_pii(text: str) -> str:
    """Remove e-mail addresses, phone numbers and SSN-like identifiers from output text."""
    if not text:
        return text
    out = text
    for pattern, replacement in _PII_PATTERNS:
        out = pattern.sub(replacement, out)
    return out


def redact_structure(value):
    """Apply redact_pii to every string inside a nested dict/list structure."""
    if isinstance(value, str):
        return redact_pii(value)
    if isinstance(value, dict):
        return {k: redact_structure(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_structure(v) for v in value]
    return value


class RunFailed(Exception):
    """Raised when a step cannot produce a complete result. Carries structured problems."""

    def __init__(self, step: int, message: str, problems: list[str] | None = None):
        super().__init__(message)
        self.step = step
        self.message = message
        self.problems = problems or []


def with_retries(fn: Callable, *, attempts: int = 3, delay: float = 2.0, transient=(OSError,), on_retry=None):
    """Call fn(); retry transient errors up to `attempts` times, then raise the last error."""
    last = None
    for n in range(1, attempts + 1):
        try:
            return fn()
        except transient as exc:  # noqa: PERF203
            last = exc
            if on_retry:
                on_retry(n, exc)
            if n < attempts:
                time.sleep(delay)
    raise last
