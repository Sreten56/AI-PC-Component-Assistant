"""Live market price search and guide helpers powered by Tavily."""

from __future__ import annotations

import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import requests
from llama_index.core.tools import FunctionTool

from src.config import get_settings

logger = logging.getLogger(__name__)

_TAVILY_SEARCH_URL = "https://api.tavily.com/search"
_REGIONS_PATH = Path(__file__).resolve().parent.parent / "data" / "regions.json"
_EUR_PER_RSD = 1.0 / 117.0
_EUR_PER_USD = 0.92
_SERBIA_QUERY_SITES = [
    "gigatron.rs",
    "bcgroup-online.com",
    "itsvet.com",
    "eponuda.com",
]


@lru_cache(maxsize=1)
def _load_regions() -> dict[str, dict[str, Any]]:
    try:
        payload = json.loads(_REGIONS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not load regions.json: %s", exc)
        return {}
    if not isinstance(payload, dict):
        return {}

    normalized: dict[str, dict[str, Any]] = {}
    for region_name, region_data in payload.items():
        if not isinstance(region_name, str) or not isinstance(region_data, dict):
            continue
        normalized[region_name.strip().lower()] = region_data
    return normalized


def _domains_for_region(region: str) -> list[str]:
    region_data = _load_regions().get((region or "").strip().lower(), {})
    domains = region_data.get("domains") if isinstance(region_data, dict) else None
    if not isinstance(domains, list):
        return []
    return [str(d).strip().lower() for d in domains if str(d).strip()]


def _build_query(component_name: str, region: str, category: str | None) -> str:
    category_suffix = f" {category}" if category and category.strip() else ""
    base_query = f"{component_name}{category_suffix} retail price {region}".strip()
    domains = _domains_for_region(region)
    if region.strip().lower() == "serbia":
        site_clause = " OR ".join(f"site:{domain}" for domain in _SERBIA_QUERY_SITES)
        return f"({site_clause}) {base_query} -site:ubuy.rs"
    if not domains:
        return base_query

    site_clause = " OR ".join(f"site:{domain}" for domain in domains)
    return f"{base_query} ({site_clause})"


def _extract_price_eur(text: str) -> float | None:
    if not text:
        return None
    patterns: list[tuple[str, float]] = [
        (r"(\d[\d\.,\s]{1,16})\s*(?:€|eur)\b", 1.0),
        (r"(\d[\d\.,\s]{1,16})\s*(?:rsd|din)\b", _EUR_PER_RSD),
        (r"(?:rsd|din)\s*(\d[\d\.,\s]{1,16})\b", _EUR_PER_RSD),
        (r"(\d[\d\.,\s]{1,16})\s*\$", _EUR_PER_USD),
    ]
    for pattern, multiplier in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        raw = re.sub(r"\s+", "", match.group(1).strip())
        if "." in raw and "," in raw:
            if raw.rfind(",") > raw.rfind("."):
                raw = raw.replace(".", "").replace(",", ".")
            else:
                raw = raw.replace(",", "")
        elif "," in raw:
            parts = raw.split(",")
            raw = raw.replace(",", "") if len(parts[-1]) == 3 else raw.replace(",", ".")
        elif "." in raw:
            parts = raw.split(".")
            raw = raw.replace(".", "") if len(parts[-1]) == 3 else raw
        try:
            return round(float(raw) * multiplier, 2)
        except ValueError:
            continue
    return None


def _extract_domain(url: str) -> str:
    try:
        netloc = urlparse(url).netloc
    except Exception:  # noqa: BLE001
        netloc = ""
    return netloc.lower().replace("www.", "")


def _normalize_listing_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    url = value.strip()
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return url


def _clean_product_name(result: dict[str, Any]) -> str:
    title = str(result.get("title", "")).strip()
    title = re.sub(r"\s*\|\s*.*$", "", title)
    return title or str(result.get("url", "")).strip() or "Unknown Product"


def _extract_image_url(result: dict[str, Any], category: str | None) -> str:
    result_images = result.get("images")
    if isinstance(result_images, list):
        for image in result_images:
            if isinstance(image, str) and image.startswith("http"):
                return image
    for key in ("image", "thumbnail", "thumbnail_url"):
        value = result.get(key)
        if isinstance(value, str) and value.startswith("http"):
            return value
    category_label = (category or "pc component").replace(" ", "+")
    return f"https://placehold.co/400x240/0f172a/e2e8f0?text={category_label}"


def _tavily_search(
    query: str,
    region: str,
    limit: int,
    *,
    include_images: bool = True,
    include_answer: bool = False,
    search_depth: str = "advanced",
) -> dict[str, Any]:
    settings = get_settings()
    payload: dict[str, Any] = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "search_depth": search_depth,
        "max_results": max(3, min(25, int(limit))),
        "include_answer": include_answer,
        "include_images": include_images,
        "include_raw_content": False,
    }
    region_domains = _domains_for_region(region)
    if region_domains:
        payload["include_domains"] = region_domains

    response = requests.post(_TAVILY_SEARCH_URL, json=payload, timeout=25)
    response.raise_for_status()
    body = response.json()
    return body if isinstance(body, dict) else {"results": []}


def search_pc_prices(
    component_name: str,
    max_price: Optional[float] = None,
    limit: int = 6,
    region: str = "Serbia",
    category: str | None = None,
) -> list[dict]:
    """Search live PC component listings using Tavily and region profiles."""
    if not isinstance(component_name, str) or not component_name.strip():
        return []

    region = region.strip() or "Serbia"
    query = _build_query(component_name.strip(), region, category)
    try:
        payload = _tavily_search(
            query=query,
            region=region,
            limit=limit * 4,
            include_images=True,
            include_answer=False,
            search_depth="advanced",
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Tavily search failed for %s (%s)", component_name, region)
        raise RuntimeError("Service unavailable.") from exc

    results = payload.get("results", [])
    top_images = payload.get("images", []) if isinstance(payload.get("images"), list) else []

    products: list[dict[str, Any]] = []
    for index, result in enumerate(results):
        if not isinstance(result, dict):
            continue
        title = _clean_product_name(result)
        text_blob = " ".join(str(result.get(k, "")) for k in ("title", "content", "raw_content"))
        price_eur = _extract_price_eur(f"{title} {text_blob}")
        if max_price is not None and price_eur is not None and price_eur > float(max_price):
            continue

        listing_url = _normalize_listing_url(result.get("url"))

        thumbnail = _extract_image_url(result, category)
        if index < len(top_images):
            maybe = top_images[index]
            if isinstance(maybe, str) and maybe.startswith("http"):
                thumbnail = maybe

        products.append(
            {
                "name": title,
                "category": category or "Live Listing",
                "price_eur": price_eur,
                "store": _extract_domain(listing_url or "") or region,
                "url": listing_url,
                "thumbnail": thumbnail,
                "region": region,
            }
        )
        if len(products) >= max(1, int(limit)):
            break

    products.sort(
        key=lambda x: x.get("price_eur") if isinstance(x.get("price_eur"), (float, int)) else 10**9
    )
    return products


def search_step_illustration(step_text: str, region: str = "global") -> str:
    """Search for a relevant image URL for a PC assembly step."""
    query = f"{step_text} PC assembly diagram tutorial image"
    try:
        payload = _tavily_search(
            query=query,
            region=region,
            limit=5,
            include_images=True,
            include_answer=False,
            search_depth="basic",
        )
    except Exception:  # noqa: BLE001
        payload = {}

    images = payload.get("images")
    if isinstance(images, list):
        for image in images:
            if isinstance(image, str) and image.startswith("http"):
                return image

    results = payload.get("results", [])
    if isinstance(results, list):
        for result in results:
            if isinstance(result, dict):
                candidate = _extract_image_url(result, "assembly")
                if candidate.startswith("http"):
                    return candidate
    return ""


def search_guide_answer(question: str, region: str = "global") -> str:
    """Fetch a concise real-time answer for a specific assembly question."""
    query = f"{question} desktop pc assembly instructions"
    try:
        payload = _tavily_search(
            query=query,
            region=region,
            limit=5,
            include_images=False,
            include_answer=True,
            search_depth="advanced",
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Guide Tavily answer failed: %s", exc)
        return "I could not fetch live guidance right now. Please try again."

    answer = payload.get("answer")
    if isinstance(answer, str) and answer.strip():
        return answer.strip()

    results = payload.get("results", [])
    snippets: list[str] = []
    if isinstance(results, list):
        for result in results[:3]:
            if not isinstance(result, dict):
                continue
            content = str(result.get("content", "")).strip()
            if content:
                snippets.append(content)
    if snippets:
        return " ".join(snippets)[:900]
    return "No live instructions were found for this specific question."


search_pc_prices_tool = FunctionTool.from_defaults(
    fn=search_pc_prices,
    name="search_pc_prices",
    description=(
        "Search live PC component listings using Tavily. "
        "Loads region domain preferences from regions.json and prioritizes those stores first."
    ),
)

