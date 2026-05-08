"""Streamlit entry point for the PC AI Component Assistant.

Default appearance (including dark theme) is configured in ``.streamlit/config.toml``.
Users can switch theme under Streamlit menu → Settings → Theme.
"""

from __future__ import annotations

import logging

import streamlit as st

from src.ui.chat_view import render_chat_view
from src.ui.guide_view import render_guide_view
from src.ui.search_view import render_search_view
from src.ui.sidebar import render_sidebar

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    st.set_page_config(
        page_title="PC AI Component Assistant",
        page_icon="🧩",
        layout="wide",
        menu_items={
            "Get Help": None,
            "Report a bug": None,
            "About": None,
        },
    )

    mode = render_sidebar()

    if mode == "Search":
        render_search_view()
    elif mode == "Chat":
        render_chat_view()
    elif mode == "Assembly Guide":
        render_guide_view()
    else:
        st.error(f"Unknown mode: {mode}")


main()
