"""Assembly guide view: tool-less agent that walks the user through a build."""

from __future__ import annotations

import logging
import re

import streamlit as st

from src.agent import AgentBuildError, build_guide_agent
from src.tools.price_search import search_step_illustration

logger = logging.getLogger(__name__)

_AGENT_KEY = "guide_agent"
_HISTORY_KEY = "guide_history"
_IMAGE_CACHE_KEY = "guide_image_cache"

_DEFAULT_PROMPT = (
    "Give me the full numbered assembly walkthrough for a standard ATX build. "
    "Keep it beginner-friendly."
)

_PLACEHOLDER_BASE = "https://placehold.co/1200x675/111827/e5e7eb?text="


def _placeholder_for(step_title: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9 ]+", "", step_title).strip().replace(" ", "+")
    return f"{_PLACEHOLDER_BASE}{slug or 'Step'}"


def _step_image(step_title: str, step_body: str) -> str:
    query = f"{step_title} {step_body}".strip()
    cache = st.session_state.setdefault(_IMAGE_CACHE_KEY, {})
    if query in cache:
        return cache[query]
    image = search_step_illustration(query, region="global")
    if image and image.startswith("http"):
        cache[query] = image
        return image
    fallback = _placeholder_for(step_title)
    cache[query] = fallback
    return fallback


def _split_steps(answer: str) -> list[tuple[str, str]]:
    """Split a numbered-list answer into ``(title, body)`` pairs.

    Falls back to a single ``("Walkthrough", answer)`` pair when no list is
    detected, so the UI never renders empty.
    """
    pattern = re.compile(r"(?m)^\s*(?:\*\*\s*)?(\d+)[.)]\s*")
    matches = list(pattern.finditer(answer))
    if len(matches) < 2:
        return [("Walkthrough", answer.strip())]

    steps: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(answer)
        chunk = answer[start:end].strip().rstrip("*").strip()
        first_line, _, rest = chunk.partition("\n")
        title = first_line.strip().rstrip(":").strip("* ")
        body = rest.strip()
        steps.append((f"{match.group(1)}. {title}", body))
    return steps


def _get_agent():
    if _AGENT_KEY not in st.session_state:
        try:
            st.session_state[_AGENT_KEY] = build_guide_agent()
        except AgentBuildError as exc:
            st.error(str(exc))
            return None
    return st.session_state[_AGENT_KEY]


def _render_steps(answer: str) -> None:
    steps = _split_steps(answer)
    for title, body in steps:
        with st.container(border=True):
            st.markdown(f"### {title}")
            cols = st.columns([1, 2])
            with cols[0]:
                st.image(_step_image(title, body), use_container_width=True)
            with cols[1]:
                if body:
                    st.markdown(body)
                else:
                    st.caption("(see title)")


def render_guide_view() -> None:
    st.header("Assembly Guide")
    st.write(
        "Get a numbered, beginner-friendly walkthrough for assembling a desktop PC. "
        "Ask follow-up questions about specific parts at any time."
    )

    if _HISTORY_KEY not in st.session_state:
        st.session_state[_HISTORY_KEY] = []

    col_run, col_reset = st.columns([2, 1])
    with col_run:
        run_default = st.button(
            "Generate full walkthrough", type="primary", use_container_width=True
        )
    with col_reset:
        if st.button("Reset guide", use_container_width=True):
            st.session_state.pop(_AGENT_KEY, None)
            st.session_state[_HISTORY_KEY] = []
            st.session_state[_IMAGE_CACHE_KEY] = {}
            st.rerun()

    agent = _get_agent()
    if agent is None:
        return

    user_message = st.chat_input("Ask about a step or part (e.g. 'how to mount the CPU cooler?')")

    prompt: str | None = None
    if run_default:
        prompt = _DEFAULT_PROMPT
    elif user_message:
        prompt = user_message

    if prompt:
        with st.spinner("Drafting the assembly steps..."):
            try:
                response = agent.chat(prompt)
            except Exception as exc:  # noqa: BLE001 - surface guide failure
                logger.exception("Guide agent chat failed")
                st.error(
                    f"The guide could not respond: {exc}. "
                    "Check the UkisAI endpoint and try again."
                )
                return
        st.session_state[_HISTORY_KEY].append({"prompt": prompt, "answer": str(response)})

    history = st.session_state.get(_HISTORY_KEY, [])
    if not history:
        st.info("Click *Generate full walkthrough* or ask a question to begin.")
        return

    for entry in history:
        st.markdown(f"**Question:** {entry['prompt']}")
        _render_steps(entry["answer"])
        st.divider()
