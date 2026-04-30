"""Sidebar navigation."""

from __future__ import annotations

import streamlit as st

MODES = ("Search", "Chat", "Assembly Guide")


def render_sidebar() -> str:
    with st.sidebar:
        st.title("PC AI Assistant")
        st.caption("Component prices, build advice, and assembly help.")
        mode = st.radio(
            "Mode",
            MODES,
            index=0,
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown(
            "**About**\n\n"
            "- *Search*: look up component prices.\n"
            "- *Chat*: get a budget-tailored build.\n"
            "- *Assembly Guide*: step-by-step build help."
        )
    return mode
