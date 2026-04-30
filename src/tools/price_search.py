"""Live market price search and illustration helpers powered by Tavily."""

from __future__ import annotations

import logging
import re
from urllib.parse import urlparse
from typing import Any, Optional

import requests
from llama_index.core.tools import FunctionTool

from src.config import get_settings

logger = logging.getLogger(__name__)

_TAVILY_SEARCH_URL = "https://api.tavily.com/search"
_SERBIA_DOMAINS = [
    "itsvet.com",
    "eponuda.com",
    "kupujemprodajem.com",
    "gigatron.rs",
    "bcgroup-online.com",
]
_REGION_RETAILERS: dict[str, list[str]] = {
    "germany": ["mindfactory.de", "alternate.de", "notebooksbilliger.de"],
    "france": ["ldlc.com", "materiel.net", "fnac.com"],
    "uk": ["scan.co.uk", "overclockers.co.uk", "currys.co.uk"],
    "united kingdom": ["scan.co.uk", "overclockers.co.uk", "currys.co.uk"],
    "usa": ["newegg.com", "bestbuy.com", "microcenter.com"],
    "united states": ["newegg.com", "bestbuy.com", "microcenter.com"],
}
_COMPONENT_BLACKLIST = [
    "laptop",
    "notebook",
    "desktop pc",
    "prebuilt",
    "all-in-one",
    "gaming pc",
]
_EUR_PER_RSD = 1.0 / 117.0
_EUR_PER_USD = 0.92


def _extract_price_eur(text: str) -> float | None:
    if not text:
        return None

    patterns: list[tuple[str, float]] = [
        (r"(\d[\d\.,\s]{1,12})\s*(?:€|eur)\b", 1.0),
        (r"(\d[\d\.,\s]{1,12})\s*(?:rsd|din)\b", _EUR_PER_RSD),
        (r"(?:rsd|din)\s*(\d[\d\.,\s]{1,12})\b", _EUR_PER_RSD),
        (r"(\d[\d\.,\s]{1,12})\s*\$", _EUR_PER_USD),
    ]
    for pattern, multiplier in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        raw = match.group(1).strip().replace(" ", "")
        raw = raw.replace(".", "").replace(",", ".")
        try:
            return round(float(raw) * multiplier, 2)
        except ValueError:
            continue
    return None


def _clean_product_name(result: dict[str, Any]) -> str:
    title = str(result.get("title", "")).strip()
    title = re.sub(r"\s*\|\s*.*$", "", title)
    return title or str(result.get("url", "")).strip() or "Unknown Product"


def _extract_domain(url: str) -> str:
    try:
        netloc = urlparse(url).netloc
    except Exception:  # noqa: BLE001
        netloc = ""
    return netloc.lower().replace("www.", "")


def _is_component_query(component_name: str) -> bool:
    query = component_name.lower()
    component_markers = [
        "ryzen",
        "core i",
        "rtx",
        "radeon",
        "ddr",
        "ssd",
        "nvme",
        "psu",
        "motherboard",
        "gpu",
        "cpu",
        "cooler",
    ]
    return any(marker in query for marker in component_markers) or bool(re.search(r"\d{3,5}", query))


def _required_tokens(component_name: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9\+\-]+", component_name.lower())
    return [tok for tok in tokens if len(tok) >= 3 or tok.isdigit()]


def _matches_required_tokens(title: str, required: list[str]) -> bool:
    title_lc = title.lower()
    # Strict logic: every meaningful token from query must appear in title.
    return all(token in title_lc for token in required)


def _is_blacklisted(text: str) -> bool:
    text_lc = text.lower()
    return any(keyword in text_lc for keyword in _COMPONENT_BLACKLIST)


def _build_query(component_name: str, region: str, category: str | None) -> str:
    category_suffix = f" {category}" if category and category.strip() else ""
    return f"{component_name}{category_suffix} price buy {region}".strip()


def _domains_for_region(region: str) -> list[str] | None:
    region_lc = (region or "").strip().lower()
    if region_lc == "serbia":
        return _SERBIA_DOMAINS
    if region_lc in _REGION_RETAILERS:
        return _REGION_RETAILERS[region_lc]
    return None


def _safe_logo_url(domain: str) -> str:
    if domain:
        return f"https://img.logo.dev/{domain}?format=png&size=256"
    return "https://placehold.co/400x240/0f172a/e2e8f0?text=PC+Component"


def _extract_image_url(result: dict[str, Any], fallback_domain: str, category: str | None) -> str:
    # Tavily can return images on each result and/or top-level; we prefer direct URLs.
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
    return _safe_logo_url(fallback_domain) or (
        f"https://placehold.co/400x240/0f172a/e2e8f0?text={category_label}"
    )


def _tavily_search(
    query: str,
    region: str,
    limit: int,
    include_images: bool = True,
) -> dict[str, Any]:
    settings = get_settings()
    payload: dict[str, Any] = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "search_depth": "advanced",
        "max_results": max(3, min(25, int(limit))),
        "include_answer": False,
        "include_images": include_images,
        "include_raw_content": False,
    }
    domains = _domains_for_region(region)
    if domains:
        payload["include_domains"] = domains
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
    """Search live PC component listings using Tavily with strict anti-noise logic."""
    if not isinstance(component_name, str) or not component_name.strip():
        return []

    region = region.strip() or "Serbia"
    query = _build_query(component_name.strip(), region, category)
    required_tokens = _required_tokens(component_name)
    strict_component_mode = _is_component_query(component_name)

    try:
        payload = _tavily_search(query=query, region=region, limit=limit * 4, include_images=True)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Tavily search failed for %s (%s)", component_name, region)
        raise RuntimeError(f"Live search failed: {exc}") from exc

    results = payload.get("results", [])
    top_images = payload.get("images", []) if isinstance(payload.get("images"), list) else []

    products: list[dict[str, Any]] = []
    for index, result in enumerate(results):
        if not isinstance(result, dict):
            continue
        title = _clean_product_name(result)
        text_blob = " ".join(str(result.get(k, "")) for k in ("title", "content", "raw_content"))
        merged_text = f"{title} {text_blob}"
        if strict_component_mode and _is_blacklisted(merged_text):
            continue
        if required_tokens and not _matches_required_tokens(title, required_tokens):
            continue

        price_eur = _extract_price_eur(merged_text)
        if max_price is not None:
            if price_eur is None or price_eur > float(max_price):
                continue

        url = str(result.get("url", "")).strip()
        if not url:
            continue
        domain = _extract_domain(url)
        thumbnail = _extract_image_url(result, domain, category)
        if "logo.dev" in thumbnail and index < len(top_images):
            maybe_img = top_images[index]
            if isinstance(maybe_img, str) and maybe_img.startswith("http"):
                thumbnail = maybe_img

        products.append(
            {
                "name": title,
                "category": category or "Live Listing",
                "price_eur": price_eur,
                "store": domain or region,
                "url": url,
                "thumbnail": thumbnail,
                "region": region,
            }
        )
        if len(products) >= max(1, int(limit)):
            break

    products.sort(key=lambda x: x.get("price_eur") if isinstance(x.get("price_eur"), (float, int)) else 10**9)
    return products


def search_step_illustration(step_text: str, region: str = "global") -> str:
    """Search for a relevant diagram image for a PC assembly step."""
    query = f"{step_text} PC assembly diagram tutorial image"
    try:
        payload = _tavily_search(query=query, region=region, limit=5, include_images=True)
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
                candidate = _extract_image_url(result, _extract_domain(str(result.get("url", ""))), "assembly")
                if candidate.startswith("http") and "logo.dev" not in candidate:
                    return candidate

    fallback_text = re.sub(r"[^A-Za-z0-9 ]+", "", step_text).strip().replace(" ", "+")
    return f"https://placehold.co/1200x675/111827/e5e7eb?text={fallback_text or 'PC+Assembly+Step'}"


search_pc_prices_tool = FunctionTool.from_defaults(
    fn=search_pc_prices,
    name="search_pc_prices",
    description=(
        "Search live PC component listings using Tavily. "
        "Inputs: component_name (required), optional max_price in EUR, optional region "
        "(defaults to Serbia), optional category (CPU/GPU/RAM/etc). "
        "Strictly filters out noisy results (e.g. laptop or prebuilt pages) and enforces "
        "title-token matching for component precision."
    ),
)


if __name__ == "__main__":
    import pprint

    pprint.pp(search_pc_prices("Ryzen 5 7600", limit=5, region="Serbia", category="CPU"))
