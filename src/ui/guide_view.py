import os
import sys
import pathlib
import streamlit as st
from PIL import Image

# Force path resolution for D: drive
_PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.append(str(_PROJECT_ROOT))

# Import static data
try:
    from src.data.assembly_data import ASSEMBLY_STEPS, EXTRA_ASSETS
except ImportError:
    # Fallback for complex path issues
    import src.data.assembly_data as ad
    ASSEMBLY_STEPS = ad.ASSEMBLY_STEPS
    EXTRA_ASSETS = ad.EXTRA_ASSETS

from src.tools.price_search import search_guide_answer, search_step_illustration

_HISTORY_KEY = "guide_history"

def _load_local_image(relative_path: str):
    """Pokušava da učita sliku sa diska koristeći PIL."""
    try:
        # Konstruisanje apsolutne putanje od korena projekta
        full_path = os.path.join(str(_PROJECT_ROOT), relative_path)
        if os.path.exists(full_path):
            return Image.open(full_path)
        return None
    except Exception:
        return None

def _render_static_steps(steps: list) -> None:
    """Prikazuje fiksne korake sa lokalnim slikama."""
    for step in steps:
        with st.container(border=True):
            st.markdown(f"### {step['step']}. {step['title']}")
            cols = st.columns([1, 2])
            with cols[0]:
                img = _load_local_image(step['image_path'])
                if img:
                    st.image(img, use_container_width=True)
                else:
                    st.error(f"Fajl nije nađen: {step['image_path']}")
            with cols[1]:
                st.markdown(step['text'])

def render_guide_view() -> None:
    st.header("Vodič za sklapanje računara")
    st.write("Pratite uputstva korak-po-korak sa vašim lokalnim ilustracijama.")

    if _HISTORY_KEY not in st.session_state:
        st.session_state[_HISTORY_KEY] = []

    col_run, col_reset = st.columns([2, 1])
    with col_run:
        if st.button("Pokreni kompletan vodič", type="primary", use_container_width=True):
            st.session_state[_HISTORY_KEY].append({
                "mode": "static",
                "prompt": "Full Walkthrough",
                "steps": ASSEMBLY_STEPS
            })

    with col_reset:
        if st.button("Resetuj istoriju", use_container_width=True):
            st.session_state[_HISTORY_KEY] = []
            st.rerun()

    user_message = st.chat_input("Postavite pitanje o sklapanju...")
    if user_message:
        with st.spinner("Razmišljam..."):
            local_img = None
            # Provera EXTRA_ASSETS (lokalnih slika)
            for key, path in EXTRA_ASSETS.items():
                if key.lower() in user_message.lower():
                    local_img = _load_local_image(path)
                    break
            
            answer = search_guide_answer(user_message, region="global")
            
            # Ako nema lokalne slike, traži URL preko Tavily
            display_img = local_img
            if not display_img:
                display_img = search_step_illustration(user_message, region="global")

            st.session_state[_HISTORY_KEY].append({
                "mode": "dynamic",
                "prompt": user_message,
                "answer": answer,
                "image": display_img,
            })

    # Renderovanje istorije
    for entry in st.session_state[_HISTORY_KEY]:
        st.markdown(f"**Zahtev:** {entry['prompt']}")
        if entry["mode"] == "static":
            _render_static_steps(entry["steps"])
        else:
            with st.container(border=True):
                cols = st.columns([1, 2])
                with cols[0]:
                    if entry["image"]:
                        st.image(entry["image"], use_container_width=True)
                with cols[1]:
                    st.markdown(entry["answer"])
        st.divider()