"""Agent factories for the consultant chat and assembly guide modes."""

from __future__ import annotations

import logging
from typing import Any

from llama_index.core.agent import FunctionCallingAgent

from src.llm import get_llm
from src.prompts import ASSEMBLY_GUIDE_SYSTEM_PROMPT, CONSULTANT_SYSTEM_PROMPT
from src.tools.price_search import search_pc_prices_tool

logger = logging.getLogger(__name__)


class AgentBuildError(RuntimeError):
    """Raised when an agent cannot be constructed (config / network / SDK)."""


def _build_agent(tools: list[Any], system_prompt: str, *, verbose: bool) -> FunctionCallingAgent:
    try:
        llm = get_llm()
        return FunctionCallingAgent.from_tools(
            tools=tools,
            llm=llm,
            system_prompt=system_prompt,
            verbose=verbose,
        )
    except Exception as exc:  # noqa: BLE001 - surface every init failure with context
        logger.exception("Failed to build agent")
        raise AgentBuildError(
            f"Could not initialise the agent: {exc}. "
            "Check your .env (UKISAI_API_BASE, UKISAI_API_KEY, optional UKISAI_MODEL) "
            "and that the UkisAI endpoint is reachable."
        ) from exc


def build_consultant_agent() -> FunctionCallingAgent:
    """Return a FunctionCallingAgent that can call `search_pc_prices`."""
    return _build_agent(
        tools=[search_pc_prices_tool],
        system_prompt=CONSULTANT_SYSTEM_PROMPT,
        verbose=True,
    )


def build_guide_agent() -> FunctionCallingAgent:
    """Return a tool-less agent for the assembly guide."""
    return _build_agent(
        tools=[],
        system_prompt=ASSEMBLY_GUIDE_SYSTEM_PROMPT,
        verbose=False,
    )
