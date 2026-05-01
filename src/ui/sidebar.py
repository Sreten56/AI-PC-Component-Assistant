"""Sidebar navigation."""

from __future__ import annotations

import streamlit as st

MODES = ("Search", "Chat", "Assembly Guide")


def _apply_custom_theme(theme_mode: str) -> None:
    if theme_mode == "☀️ Light":
        css = """
        <style>
        .stApp {
            background-color: #f5f7fb;
            color: #0f172a;
        }
        section[data-testid="stSidebar"] {
            background-color: #e9eef8;
            color: #0f172a;
        }
        div[data-testid="stMarkdownContainer"], label, p, span, h1, h2, h3 {
            color: #0f172a !important;
        }
        </style>
        """
    else:
        css = """
        <style>
        .stApp {
            background-color: #0b1220;
            color: #e2e8f0;
        }
        section[data-testid="stSidebar"] {
            background-color: #111827;
            color: #e2e8f0;
        }
        div[data-testid="stMarkdownContainer"], label, p, span, h1, h2, h3 {
            color: #e2e8f0 !important;
        }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)


def render_sidebar() -> str:
    if "ui_theme_mode" not in st.session_state:
        st.session_state["ui_theme_mode"] = "🌙 Dark"

    with st.sidebar:
        st.title("PC AI Assistant")
        st.caption("Component prices, build advice, and assembly help.")
        theme_choice = st.radio(
            "Theme Mode",
            ("🌙 Dark", "☀️ Light"),
            index=0 if st.session_state["ui_theme_mode"] == "🌙 Dark" else 1,
            horizontal=True,
        )
        st.session_state["ui_theme_mode"] = theme_choice
        st.divider()
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
        st.sidebar.markdown("<br>" * 10, unsafe_allow_html=True)
        st.caption(
            "This is a student project created for educational purposes. "
            "It is not a commercial application."
        )

    _apply_custom_theme(st.session_state["ui_theme_mode"])
    return mode
