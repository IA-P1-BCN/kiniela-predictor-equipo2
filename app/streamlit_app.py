import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kiniela.config import CLASS_NAMES  # noqa: E402

st.set_page_config(page_title="Kiniela Predictor", page_icon="⚽", layout="centered")

st.title("Kiniela Predictor")
st.caption("Equipo 2 · clasificación del tipo de resultado")

st.info(
    "La aplicación todavía no predice: no hay modelo entrenado ni dataset en el repositorio. "
    "Cuando exista un artefacto en models/, esta pantalla mostrará la clase y las seis probabilidades."
)

st.subheader("Clases")
for class_id, name in CLASS_NAMES.items():
    st.write(f"**{class_id}.** {name}")

st.subheader("Partido")
col_home, col_away = st.columns(2)
with col_home:
    st.text_input("Equipo local", placeholder="Nombre del local")
with col_away:
    st.text_input("Equipo visitante", placeholder="Nombre del visitante")

st.button("Predecir", disabled=True, help="Se activa cuando haya un modelo en models/.")
