"""Assembly guide with static multilingual steps and local images."""

from __future__ import annotations

import logging
import os
import pathlib
from copy import deepcopy
from io import BytesIO
from typing import Any

import requests
import streamlit as st
from PIL import Image

from src.data.assembly_data import ASSEMBLY_STEPS_BY_LANG, EXTRA_ASSETS
from src.tools.price_search import search_guide_answer, search_step_illustration
from src.ui.sanitize import sanitize_chat_input

logger = logging.getLogger(__name__)

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_STATIC_IMAGES_ROOT = (_PROJECT_ROOT / "src" / "static" / "images").resolve()
_PLACEHOLDER_PATH = "src/static/images/placeholder.jpg"
_HISTORY_KEY = "guide_history"
_LANG_OPTIONS = (
    ("English", "EN"),
    ("Serbian", "SR"),
    ("German", "GER"),
    ("French", "FR"),
    ("Spanish", "ESP"),
    ("Russian", "RUS"),
)
_LANGUAGE_NAMES = {
    "EN": "English",
    "SR": "Serbian",
    "GER": "German",
    "FR": "French",
    "ESP": "Spanish",
    "RUS": "Russian",
}


def _ui_strings(language_code: str) -> dict[str, str]:
    if language_code == "SR":
        return {
            "header": "Vodič za sklapanje računara",
            "blurb": "Pratite uputstva korak-po-korak sa lokalnim ilustracijama.",
            "empty_hint": "Kliknite **Pokreni kompletan vodič** ili postavite pitanje ispod.",
            "run": "Pokreni kompletan vodič",
            "reset": "Resetuj istoriju",
            "chat_placeholder": "Postavite pitanje o sklapanju...",
            "request_label": "Zahtev",
            "missing_file": "Fajl nije nađen",
            "translating": "Prevodim korake…",
            "thinking": "Razmišljam…",
            "translate_error": "Prevod nije uspeo — prikazani su izvorni srpski koraci.",
        }
    if language_code == "GER":
        return {
            "header": "PC-Montageanleitung",
            "blurb": "Folgen Sie den Schritt-fur-Schritt-Anweisungen mit lokalen Bildern.",
            "empty_hint": "Klicken Sie auf **Komplette Anleitung starten** oder stellen Sie unten eine Frage.",
            "run": "Komplette Anleitung starten",
            "reset": "Verlauf zurucksetzen",
            "chat_placeholder": "Stellen Sie eine Frage zur Montage...",
            "request_label": "Anfrage",
            "missing_file": "Datei nicht gefunden",
            "thinking": "Denke...",
        }
    if language_code == "FR":
        return {
            "header": "Guide d'assemblage PC",
            "blurb": "Suivez les etapes avec des illustrations locales.",
            "empty_hint": "Cliquez sur **Lancer le guide complet** ou posez une question ci-dessous.",
            "run": "Lancer le guide complet",
            "reset": "Reinitialiser l'historique",
            "chat_placeholder": "Posez une question sur l'assemblage...",
            "request_label": "Demande",
            "missing_file": "Fichier introuvable",
            "thinking": "Analyse...",
        }
    if language_code == "ESP":
        return {
            "header": "Guia de ensamblaje de PC",
            "blurb": "Sigue los pasos con imagenes locales.",
            "empty_hint": "Pulsa **Ejecutar guia completa** o haz una pregunta abajo.",
            "run": "Ejecutar guia completa",
            "reset": "Reiniciar historial",
            "chat_placeholder": "Haz una pregunta sobre el ensamblaje...",
            "request_label": "Solicitud",
            "missing_file": "Archivo no encontrado",
            "thinking": "Pensando...",
        }
    if language_code == "RUS":
        return {
            "header": "Руководство по сборке ПК",
            "blurb": "Следуйте пошаговым инструкциям с локальными изображениями.",
            "empty_hint": "Нажмите **Запустить полное руководство** или задайте вопрос ниже.",
            "run": "Запустить полное руководство",
            "reset": "Сбросить историю",
            "chat_placeholder": "Задайте вопрос по сборке...",
            "request_label": "Запрос",
            "missing_file": "Файл не найден",
            "thinking": "Обрабатываю...",
        }
    return {
        "header": "PC Assembly Guide",
        "blurb": "Follow step-by-step instructions with local illustrations.",
        "empty_hint": "Click **Run full walkthrough** or ask a question below.",
        "run": "Run full walkthrough",
        "reset": "Reset history",
        "chat_placeholder": "Ask a question about assembly…",
        "request_label": "Request",
        "missing_file": "File not found",
        "thinking": "Thinking...",
    }


def _resolve_local_image_path(relative_path: str) -> str | None:
    candidate = (_PROJECT_ROOT / relative_path).resolve()
    # Block path traversal and restrict reads to src/static/images.
    try:
        candidate.relative_to(_STATIC_IMAGES_ROOT)
    except ValueError:
        logger.warning("Blocked non-static image path: %s", relative_path)
        return None
    if not candidate.exists():
        return None
    ext = candidate.suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        logger.warning("Unsupported local image extension: %s", candidate)
        return None
    return str(candidate)


def _load_local_image(relative_path: str) -> Image.Image | None:
    """Load local image using project-root-joined relative path."""
    full_path = _resolve_local_image_path(relative_path)
    if not full_path:
        return None
    try:
        with Image.open(full_path) as img:
            return img.copy()
    except OSError:
        logger.warning("Failed to open local image: %s", full_path)
        return None


def _load_local_image_object(relative_path: str) -> Image.Image | None:
    return _load_local_image(relative_path)


def _get_placeholder_image() -> Image.Image | None:
    placeholder = _load_local_image_object(_PLACEHOLDER_PATH)
    if placeholder is None:
        logger.warning("Placeholder image not found at: %s", _PLACEHOLDER_PATH)
    return placeholder


def dynamic_step_image(image_candidate: str | None) -> Image.Image | str | None:
    """Return a valid dynamic image or local placeholder if unavailable."""
    candidate = (image_candidate or "").strip()
    if not candidate:
        return _get_placeholder_image()

    if candidate.startswith(("http://", "https://")):
        try:
            resp = requests.get(candidate, timeout=6)
            resp.raise_for_status()
            with Image.open(BytesIO(resp.content)) as img:
                return img.copy()
        except Exception:  # noqa: BLE001
            logger.warning("Dynamic URL image failed, using placeholder: %s", candidate)
            return _get_placeholder_image()

    local_img = _load_local_image_object(candidate)
    return local_img or _get_placeholder_image()


def _steps_for_display_language(language_code: str) -> list[dict[str, Any]]:
    steps = ASSEMBLY_STEPS_BY_LANG.get(language_code) or ASSEMBLY_STEPS_BY_LANG["EN"]
    return deepcopy(steps)


def _build_master_language_query(user_message: str, language_code: str) -> str:
    target_language = _LANGUAGE_NAMES.get(language_code, "English")
    detailed_prefix = (
        "Pruži detaljno, stručno i opširno uputstvo za sledeći zadatak sklapanja: "
        f"{user_message}"
    )
    return (
        f"{detailed_prefix}\n"
        f"Answer strictly in {target_language}. "
        "Do not switch language. "
        "If the question is off-topic, clearly explain scope limits."
    )


def _split_special_note(answer: str) -> tuple[str, str]:
    marker = "Note: I am an assistant specialized"
    text = (answer or "").strip()
    idx = text.find(marker)
    if idx == -1:
        return text, ""
    short_answer = text[:idx].strip()
    note = text[idx:].strip()
    return short_answer, note


def _render_static_steps(steps: list[dict[str, Any]], labels: dict[str, str]) -> None:
    for step in steps:
        with st.container(border=True):
            st.markdown(f"### {step['step']}. {step['title']}")
            cols = st.columns([1, 2])
            with cols[0]:
                step_image = _load_local_image(step.get("image_path", ""))
                if step_image is None:
                    step_image = _get_placeholder_image()
                    st.warning(f"{labels['missing_file']}: {step.get('image_path', '')}")
                if step_image is not None:
                    st.image(step_image, use_container_width=True)
            with cols[1]:
                st.markdown(step["text"])


def render_guide_view() -> None:
    selected_language = st.selectbox(
        "Guide language / Jezik vodiča",
        [label for label, _ in _LANG_OPTIONS],
        index=0,
        key="guide_language_select",
    )
    language_code = dict(_LANG_OPTIONS).get(selected_language, "EN")
    labels = _ui_strings(language_code)

    st.header(labels["header"])
    st.write(labels["blurb"])

    if _HISTORY_KEY not in st.session_state:
        st.session_state[_HISTORY_KEY] = []

    col_run, col_reset = st.columns([2, 1])
    with col_run:
        if st.button(labels["run"], type="primary", use_container_width=True):
            steps = _steps_for_display_language(language_code)
            entry: dict[str, Any] = {
                "mode": "static",
                "prompt": labels["run"],
                "steps": steps,
                "language": language_code,
            }
            st.session_state[_HISTORY_KEY].append(entry)

    with col_reset:
        if st.button(labels["reset"], use_container_width=True):
            st.session_state[_HISTORY_KEY] = []
            st.rerun()

    user_message_raw = st.chat_input(labels["chat_placeholder"])
    user_message = sanitize_chat_input(user_message_raw or "")
    if user_message:
        with st.spinner(labels["thinking"]):
            local_img_path = None
            for key, path in EXTRA_ASSETS.items():
                if key.lower() in user_message.lower():
                    local_img_path = _resolve_local_image_path(path)
                    break

            answer = search_guide_answer(
                _build_master_language_query(user_message, language_code),
                region="global",
            )
            short_answer, special_note = _split_special_note(answer)

            display_img: Any = local_img_path
            if not display_img:
                display_img = search_step_illustration(user_message, region="global")
            display_img = dynamic_step_image(display_img)

            st.session_state[_HISTORY_KEY].append(
                {
                    "mode": "dynamic",
                    "prompt": user_message,
                    "answer": short_answer or answer,
                    "special_note": special_note,
                    "image": display_img,
                    "language": language_code,
                }
            )

    history = st.session_state.get(_HISTORY_KEY, [])
    if not history:
        st.info(labels["empty_hint"])
        return

    for entry in history:
        st.markdown(f"**{labels['request_label']}:** {entry['prompt']}")
        if entry["mode"] == "static":
            _render_static_steps(entry["steps"], labels)
        else:
            with st.container(border=True):
                cols = st.columns([1, 2])
                with cols[0]:
                    image = entry.get("image")
                    if image:
                        st.image(image, use_container_width=True)
                    else:
                        placeholder = _get_placeholder_image()
                        if placeholder is not None:
                            st.image(placeholder, use_container_width=True)
                with cols[1]:
                    st.markdown(entry.get("answer", ""))
                    if entry.get("special_note"):
                        st.info(entry["special_note"])
        st.divider()
