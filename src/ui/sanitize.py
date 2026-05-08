"""Lightweight sanitization for user-supplied text shown in the UI."""

from __future__ import annotations

import re

_SCRIPT_PATTERNS = (
    r"(?is)<script[^>]*>.*?</script>",
    r"(?i)<\s*script\b[^>]*>",
    r"(?i)</\s*script\s*>",
)

_SQL_KEYWORDS = (
    "DROP",
    "DELETE",
    "SELECT",
    "UPDATE",
    "INSERT",
    "UNION",
    "TRUNCATE",
    "ALTER",
)

_PROMPT_INJECTION_PATTERNS = (
    r"(?i)\bignore\s+previous\s+instructions\b",
    r"(?i)\bsystem\s+override\b",
    r"(?i)\bdeveloper\s+mode\b",
    r"(?i)\bdisregard\s+all\s+prior\b",
    r"(?i)\bprompt\s+injection\b",
)


def sanitize_chat_input(text: str) -> str:
    """Strip common script/SQL/prompt-injection patterns from UI inputs."""
    if not text or not isinstance(text, str):
        return ""
    cleaned = text
    for pattern in _SCRIPT_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned)
    for keyword in _SQL_KEYWORDS:
        cleaned = re.sub(rf"(?i)\b{keyword}\b", "", cleaned)
    for pattern in _PROMPT_INJECTION_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned.strip()
