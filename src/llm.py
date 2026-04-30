"""UkisAI LLM initialisation.

Discovers an available model via the OpenAI-compatible `/models` endpoint
(falling back to `UKISAI_MODEL` from the environment) and wraps it in a
LlamaIndex `OpenAILike` client.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from urllib.parse import urljoin

import requests
from llama_index.llms.openai_like import OpenAILike

from src.config import ConfigError, Settings, get_settings

logger = logging.getLogger(__name__)

# Models we'd rather pick if the server returns a list. The first match wins;
# if none match, we just take the first model the server reports.
_PREFERRED_MODEL_HINTS = (
    "gpt-4o",
    "gpt-4",
    "llama",
    "mistral",
    "qwen",
)


def _models_endpoint(api_base: str) -> str:
    base = api_base if api_base.endswith("/") else api_base + "/"
    return urljoin(base, "models")


def discover_model(settings: Settings | None = None, timeout: float = 10.0) -> str:
    """Return the model id to use, preferring the env override.

    Raises ``ConfigError`` only if no model can be determined at all.
    """
    settings = settings or get_settings()

    if settings.model:
        return settings.model

    url = _models_endpoint(settings.api_base)
    headers = {"Authorization": f"Bearer {settings.api_key}"}

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise ConfigError(
            "Could not discover a model from "
            f"{url}: {exc}. Set UKISAI_MODEL in .env to bypass discovery."
        ) from exc

    items = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(items, list) or not items:
        raise ConfigError(
            f"Models endpoint at {url} returned no entries. "
            "Set UKISAI_MODEL in .env to bypass discovery."
        )

    ids: list[str] = []
    for item in items:
        if isinstance(item, dict) and "id" in item:
            ids.append(str(item["id"]))
        elif isinstance(item, str):
            ids.append(item)

    if not ids:
        raise ConfigError(
            f"Models endpoint at {url} returned an unexpected shape. "
            "Set UKISAI_MODEL in .env to bypass discovery."
        )

    for hint in _PREFERRED_MODEL_HINTS:
        for model_id in ids:
            if hint.lower() in model_id.lower():
                return model_id

    return ids[0]


@lru_cache(maxsize=1)
def get_llm() -> OpenAILike:
    """Return a memoised UkisAI-backed LLM client."""
    settings = get_settings()
    model = discover_model(settings)
    logger.info("Using UkisAI model: %s", model)

    return OpenAILike(
        model=model,
        api_base=settings.api_base,
        api_key=settings.api_key,
        is_function_calling_model=True,
        is_chat_model=True,
        context_window=128000,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        llm = get_llm()
    except ConfigError as exc:
        print(f"[config error] {exc}")
        raise SystemExit(1)

    print(f"Resolved model: {llm.model}")
    try:
        reply = llm.complete("Reply with exactly: PC AI Component Assistant online.")
        print(f"LLM reply: {reply}")
    except Exception as exc:  # noqa: BLE001 - smoke test, surface anything
        print(f"[LLM call failed] {exc}")
        raise SystemExit(2)
