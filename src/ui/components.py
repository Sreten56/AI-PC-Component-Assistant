"""Shared Streamlit UI components (e.g. product cards)."""

from __future__ import annotations

from typing import Iterable, Mapping

import streamlit as st

_CARD_CSS = """
<style>
.product-thumb-wrap {
  width: 100%;
  height: 170px;
  border-radius: 10px;
  overflow: hidden;
  background: #0f172a;
  display: flex;
  align-items: center;
  justify-content: center;
}
.product-thumb-wrap img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
"""


def _format_price(value: object) -> str:
    try:
        return f"\u20ac{float(value):,.0f}"
    except (TypeError, ValueError):
        return "Price n/a"


def render_product_card(item: Mapping[str, object], *, key_prefix: str = "card") -> None:
    """Render a single product card."""
    name = str(item.get("name", "Unknown component"))
    category = str(item.get("category", ""))
    store = str(item.get("store", ""))
    url = str(item.get("url", ""))
    thumbnail = str(item.get("thumbnail", "")) or "https://placehold.co/400x300?text=No+Image"

    with st.container(border=True):
        st.markdown(_CARD_CSS, unsafe_allow_html=True)
        st.markdown(
            f'<div class="product-thumb-wrap"><img src="{thumbnail}" alt="{name}"></div>',
            unsafe_allow_html=True,
        )
        if category:
            st.caption(category)
        st.markdown(f"**{name}**")
        st.markdown(f"### {_format_price(item.get('price_eur'))}")
        if store:
            st.caption(f"Sold by {store}")
        if url:
            st.link_button("Buy Now", url, use_container_width=True)


def render_product_grid(
    items: Iterable[Mapping[str, object]],
    *,
    columns: int = 3,
    key_prefix: str = "grid",
) -> None:
    """Render a list of products as a responsive card grid."""
    materialised = list(items)
    if not materialised:
        st.info("No matching listings found. Try a different query or raise the budget.")
        return

    for row_start in range(0, len(materialised), columns):
        row = materialised[row_start : row_start + columns]
        cols = st.columns(columns, gap="medium")
        for offset, (col, item) in enumerate(zip(cols, row)):
            with col:
                render_product_card(item, key_prefix=f"{key_prefix}_{row_start + offset}")
