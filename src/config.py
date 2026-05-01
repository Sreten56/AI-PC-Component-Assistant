"""Centralised configuration from environment variables.

Values are read only from ``os.environ`` (after optional ``python-dotenv``
load of a local ``.env`` for development). Production deployments should
inject secrets via the environment and must not log raw API keys.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


def redact_secret(value: str, *, head: int = 4, tail: int = 2) -> str:
    """Return a non-reversible hint for logs; never use for authentication."""
    if not value:
        return "(empty)"
    s = str(value).strip()
    if len(s) <= head + tail:
        return "***"
    return f"{s[:head]}…{s[-tail:]}"


@dataclass(frozen=True)
class Settings:
    api_base: str
    api_key: str
    model: str | None
    tavily_api_key: str


def get_settings() -> Settings:
    api_base = os.getenv("UKISAI_API_BASE", "").strip()
    api_key = os.getenv("UKISAI_API_KEY", "").strip()
    model = os.getenv("UKISAI_MODEL", "").strip() or None
    tavily_api_key = os.getenv("TAVILY_API_KEY", "").strip()

    if not api_base:
        raise ConfigError(
            "UKISAI_API_BASE is not set. Copy .env.example to .env and fill it in."
        )
    if not api_key:
        raise ConfigError(
            "UKISAI_API_KEY is not set. Use 'dummy' if the endpoint does not need a key."
        )
    if not tavily_api_key:
        raise ConfigError(
            "TAVILY_API_KEY is not set. Add it to .env for live price search."
        )

    return Settings(
        api_base=api_base,
        api_key=api_key,
        model=model,
        tavily_api_key=tavily_api_key,
    )
