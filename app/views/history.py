"""Page: recent predictions with their feedback, and the model's live accuracy."""

import pandas as pd
import streamlit as st
from resources import class_label, get_db_engine, get_predictor, get_router, team_label
from sqlalchemy.exc import SQLAlchemyError

from kiniela.models.ab_testing import (
    CANDIDATE_CARD_NAME,
    CURRENT_CARD_NAME,
    MODELS_DIR,
    load_model_card,
    version_evidence,
)
from kiniela.storage import feedback_stats, list_history, session_scope

HISTORY_LIMIT = 50


def feedback_label(prediction) -> str:
    feedback = prediction.feedback
    if feedback is None:
        return "Pendiente"
    if feedback.is_correct:
        return "✅ Acertó"
    if feedback.actual_class is not None:
        return f"❌ Real: {class_label(feedback.actual_class)}"
    return "❌ Falló"


def show_stats(stats: dict, title: str) -> None:
    st.markdown(f"**{title}**")
    total_col, reviewed_col, accuracy_col = st.columns(3)
    total_col.metric("Predicciones", stats["predictions"])
    reviewed_col.metric("Con feedback", stats["with_feedback"])
    accuracy = stats["accuracy"]
    accuracy_col.metric("Acierto según el feedback", "—" if accuracy is None else f"{accuracy:.0%}")


def comparison_rows(session, router) -> list[dict]:
    """One row per model in the A/B test: validation metrics and live feedback."""
    models = [
        ("Actual", router.current, CURRENT_CARD_NAME),
        ("Candidato", router.candidate, CANDIDATE_CARD_NAME),
    ]
    rows = []
    for role, model, card_name in models:
        evidence = version_evidence(session, model.version, load_model_card(MODELS_DIR / card_name))
        rows.append(
            {
                "Modelo": role,
                "Versión": evidence.version,
                "F1 macro (validación)": evidence.f1_macro,
                "Gap train/validación": evidence.overfitting_gap,
                "Predicciones": evidence.predictions,
                "Con feedback": evidence.with_feedback,
                "Acierto (feedback)": evidence.accuracy,
            }
        )
    return rows


st.title("Historial")
st.caption("Las últimas predicciones y cuánto acierta el modelo según el feedback de las personas usuarias.")

try:
    with session_scope(get_db_engine()) as session:
        current_version = get_predictor().version
        overall = feedback_stats(session)
        current = feedback_stats(session, model_version=current_version)
        router = get_router()
        comparison = comparison_rows(session, router) if router.candidate is not None else []
        rows = [
            {
                "Fecha": prediction.created_at,
                "Partido": f"{team_label(prediction.home_team)} – {team_label(prediction.away_team)}",
                "Predicción": class_label(prediction.predicted_class),
                "Confianza": max(prediction.probabilities),
                "Feedback": feedback_label(prediction),
                "Modelo": prediction.model_version,
            }
            for prediction in list_history(session, limit=HISTORY_LIMIT)
        ]
except SQLAlchemyError:
    st.error("No se puede leer la base de datos en este momento.")
    st.stop()

show_stats(current, f"Modelo actual (`{current_version}`)")
show_stats(overall, "Todos los modelos")

if comparison:
    st.divider()
    st.subheader("A/B testing")
    st.dataframe(
        pd.DataFrame(comparison),
        hide_index=True,
        width="stretch",
        column_config={
            "F1 macro (validación)": st.column_config.NumberColumn(format="%.3f"),
            "Gap train/validación": st.column_config.NumberColumn(format="%.3f"),
            "Acierto (feedback)": st.column_config.NumberColumn(format="percent"),
        },
    )
    st.caption(
        "La promoción la decide `python -m kiniela.models.promote` con la regla de "
        "`docs/ab-testing.md`."
    )

st.divider()
if not rows:
    st.info("Todavía no hay predicciones. Haz la primera en la página **Predecir**.")
else:
    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        width="stretch",
        column_config={
            "Fecha": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm"),
            "Confianza": st.column_config.ProgressColumn(format="percent", min_value=0.0, max_value=1.0),
        },
    )
    st.caption(f"Se muestran como máximo las {HISTORY_LIMIT} predicciones más recientes.")
