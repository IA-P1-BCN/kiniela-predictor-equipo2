"""Kiniela Predictor: Streamlit entry point.

Run with: streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
# Reusable code lives in src/; app modules (resources, views) live next to this file
for path in (APP_DIR.parent / "src", APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

st.set_page_config(page_title="Kiniela Predictor", page_icon="⚽", layout="centered")

navigation = st.navigation(
    [
        st.Page(APP_DIR / "views" / "predict.py", title="Predecir", icon="⚽", default=True),
        st.Page(APP_DIR / "views" / "history.py", title="Historial", icon="📊"),
    ]
)
navigation.run()
