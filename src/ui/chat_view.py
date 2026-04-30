"""Chat view: build consultant agent powered by FunctionCallingAgent."""

from __future__ import annotations

import logging
from typing import Any

import streamlit as st

from src.agent import AgentBuildError, build_consultant_agent
from src.ui.components import render_product_grid

logger = logging.getLogger(__name__)

_AGENT_KEY = "consultant_agent"
_HISTORY_KEY = "consultant_history"


def _get_agent():
    if _AGENT_KEY not in st.session_state:
        try:
            st.session_state[_AGENT_KEY] = build_consultant_agent()
        except AgentBuildError as exc:
            st.error(str(exc))
            return None
    return st.session_state[_AGENT_KEY]


def _extract_tool_results(response: Any) -> list[list[dict]]:
    """Pull `search_pc_prices` outputs out of an agent response, in order."""
    sources = getattr(response, "sources", None) or []
    grids: list[list[dict]] = []
    for source in sources:
        if getattr(source, "tool_name", None) != "search_pc_prices":
            continue
        raw = getattr(source, "raw_output", None)
        if isinstance(raw, list) and raw and all(isinstance(x, dict) for x in raw):
            grids.append(raw)
    return grids


def _render_history() -> None:
    for entry in st.session_state.get(_HISTORY_KEY, []):
        with st.chat_message(entry["role"]):
            st.markdown(entry["content"])
            for grid in entry.get("product_grids", []):
                render_product_grid(grid, columns=3, key_prefix="hist")


def render_chat_view() -> None:
    st.header("Build Consultant")
    st.write(
        "Tell me your budget and what you'll do with the PC. "
        "I'll propose a balanced parts list and pull live prices for you."
    )

    if _HISTORY_KEY not in st.session_state:
        st.session_state[_HISTORY_KEY] = []

    col_reset, _ = st.columns([1, 5])
    with col_reset:
        if st.button("Reset chat", use_container_width=True):
            st.session_state.pop(_AGENT_KEY, None)
            st.session_state[_HISTORY_KEY] = []
            st.rerun()

    agent = _get_agent()
    if agent is None:
        return

    _render_history()

    user_message = st.chat_input("e.g. I have 1200\u20ac for 1440p gaming")
    if not user_message:
        return

    st.session_state[_HISTORY_KEY].append(
        {"role": "user", "content": user_message, "product_grids": []}
    )
    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and pricing parts..."):
            try:
                response = agent.chat(user_message)
            except Exception as exc:  # noqa: BLE001 - surface every chat failure
                logger.exception("Consultant agent chat failed")
                st.error(
                    f"The consultant could not respond: {exc}. "
                    "Check the UkisAI endpoint and try again."
                )
                return

        answer = str(response)
        product_grids = _extract_tool_results(response)
        st.markdown(answer)
        for grid in product_grids:
            render_product_grid(grid, columns=3, key_prefix="live")

    st.session_state[_HISTORY_KEY].append(
        {
            "role": "assistant",
            "content": answer,
            "product_grids": product_grids,
        }
    )
