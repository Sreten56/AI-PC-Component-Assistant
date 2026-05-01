"""Lightweight sanitization for user-supplied text shown in the UI."""

from __future__ import annotations

import re


def sanitize_chat_input(text: str) -> str:
    """Strip common script-injection patterns from chat-style inputs."""
    if not text or not isinstance(text, str):
        return ""
    cleaned = text
    cleaned = re.sub(r"(?is)<script[^>]*>.*?</script>", "", cleaned)
    cleaned = re.sub(r"(?i)<\s*script\b[^>]*>", "", cleaned)
    cleaned = re.sub(r"(?i)</\s*script\s*>", "", cleaned)
    return cleaned.strip()
