"""Search view: direct component look-up via the price tool."""

from __future__ import annotations

import streamlit as st

from src.tools.price_search import search_pc_prices
from src.ui.components import render_product_grid

_CATEGORIES = ["Auto", "CPU", "GPU", "Motherboard", "RAM", "SSD", "PSU", "Case", "Cooler"]


def render_search_view() -> None:
    st.header("Component Search")
    st.write("Search live local-market prices for a specific PC component.")

    with st.form("search_form", clear_on_submit=False):
        col_query, col_category, col_region = st.columns([3, 1.4, 1.8])
        with col_query:
            query = st.text_input(
                "Component",
                placeholder="e.g. RTX 4070, Ryzen 7 7800X3D, DDR5 32GB",
            )
        with col_category:
            selected_category = st.selectbox("Category", _CATEGORIES, index=0)
        with col_region:
            region = st.text_input("Region / Country", value="Serbia")

        col_toggle, col_budget = st.columns([1, 3])
        with col_toggle:
            use_max = st.toggle("Use max price", value=True)
        with col_budget:
            max_price = st.slider(
                "Max price (\u20ac)",
                min_value=50,
                max_value=5000,
                value=1200,
                step=10,
                disabled=not use_max,
            )
        submitted = st.form_submit_button("Search", use_container_width=True)

    if not submitted:
        st.caption("Hit *Search* to fetch live listings.")
        return

    if not query.strip():
        st.warning("Please enter a component to search for.")
        return

    with st.spinner("Searching the market..."):
        try:
            effective_max_price = float(max_price) if use_max else None
            effective_category = None if selected_category == "Auto" else selected_category
            refined_query = f"{query.strip()} {effective_category}" if effective_category else query.strip()
            results = search_pc_prices(
                refined_query,
                max_price=effective_max_price,
                limit=9,
                region=region.strip() or "Serbia",
                category=effective_category,
            )
        except Exception as exc:  # noqa: BLE001 - surface tool failure to user
            st.error(f"Search failed: {exc}")
            return

    filter_note = (
        f" with max \u20ac{int(max_price)}"
        if use_max
        else " with no max price filter"
    )
    category_note = f" [{selected_category}]" if selected_category != "Auto" else ""
    st.subheader(
        f"Results for \u201c{query.strip()}{category_note}\u201d in {region.strip() or 'Serbia'}{filter_note}"
    )
    render_product_grid(results, columns=3, key_prefix="search")
