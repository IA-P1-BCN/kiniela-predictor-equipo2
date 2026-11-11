"""Page: choose a match, predict its class, save it and collect feedback."""

import pandas as pd
import streamlit as st
from resources import (
    class_label,
    get_db_engine,
    get_predictor,
    get_teams,
    is_reference_model,
    team_label,
    user_message,
)
from sqlalchemy.exc import SQLAlchemyError

from kiniela.config import CLASS_NAMES
from kiniela.models.predict import predicted_class, validate_teams
from kiniela.storage import save_feedback, save_prediction, session_scope

EXAMPLE_MATCH = ("arsenal", "chelsea")


def use_example_match(teams: list[str]) -> None:
    """Fill both selectors with a known match (callback of the example button)."""
    home, away = EXAMPLE_MATCH if set(EXAMPLE_MATCH) <= set(teams) else teams[:2]
    st.session_state["home_team"], st.session_state["away_team"] = home, away


def run_prediction(home_team: str | None, away_team: str | None) -> None:
    """Predict, try to save, and keep the result in the session for the feedback form."""
    try:
        home, away = validate_teams(home_team or "", away_team or "")
        probabilities = get_predictor().predict(home, away)
        class_id = predicted_class(probabilities)
    except ValueError as error:
        st.session_state.pop("last_prediction", None)
        st.error(user_message(error))
        return

    prediction_id = None
    try:
        with session_scope(get_db_engine()) as session:
            prediction_id = save_prediction(
                session,
                home_team=home,
                away_team=away,
                inputs={"home_team": home, "away_team": away},
                probabilities=probabilities,
                model_version=get_predictor().version,
            ).id
    except SQLAlchemyError:
        st.warning("La predicción no se ha podido guardar en la base de datos. Se muestra igualmente.")

    st.session_state["last_prediction"] = {
        "id": prediction_id,
        "home": home,
        "away": away,
        "class_id": class_id,
        "probabilities": probabilities,
    }


def show_result(result: dict) -> None:
    class_id, probabilities = result["class_id"], result["probabilities"]
    st.subheader(f"{team_label(result['home'])} – {team_label(result['away'])}")
    st.metric("Clase predicha", class_label(class_id), f"{probabilities[class_id]:.0%} de probabilidad",
              delta_color="off")

    table = pd.DataFrame(
        {
            "Clase": list(CLASS_NAMES),
            "Resultado": list(CLASS_NAMES.values()),
            "Probabilidad": probabilities,
        }
    )
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        column_config={
            "Clase": st.column_config.NumberColumn(width="small"),
            "Probabilidad": st.column_config.ProgressColumn(
                format="percent", min_value=0.0, max_value=1.0
            ),
        },
    )


def show_feedback_form(result: dict) -> None:
    prediction_id = result["id"]
    if prediction_id is None:
        return
    st.divider()
    st.subheader("¿Acertó?")
    done_key = f"feedback_sent_{prediction_id}"
    if st.session_state.get(done_key):
        st.success("¡Gracias! Tu feedback se ha guardado y cuenta para el acierto del modelo.")
        return

    st.caption("Cuando se juegue el partido, dinos si la predicción fue correcta.")
    verdict = st.radio("Resultado de la predicción", ["Sí, acertó", "No, falló"], index=None,
                       horizontal=True, key=f"verdict_{prediction_id}")
    actual_class = None
    if verdict == "No, falló":
        other_classes = [c for c in CLASS_NAMES if c != result["class_id"]]
        actual_class = st.selectbox("¿Cuál fue la clase real? (opcional)", other_classes, index=None,
                                    format_func=class_label, key=f"actual_{prediction_id}")
    comment = st.text_area("Comentario (opcional)", max_chars=1000, key=f"comment_{prediction_id}")

    if st.button("Enviar feedback", key=f"send_{prediction_id}"):
        if verdict is None:
            st.error("Indica si la predicción acertó o falló.")
            return
        is_correct = verdict == "Sí, acertó"
        try:
            with session_scope(get_db_engine()) as session:
                save_feedback(session, prediction_id, is_correct=is_correct,
                              actual_class=result["class_id"] if is_correct else actual_class,
                              comment=comment)
        except ValueError as error:
            st.error(user_message(error))
            return
        except SQLAlchemyError:
            st.warning("El feedback no se ha podido guardar. Inténtalo de nuevo más tarde.")
            return
        st.session_state[done_key] = True
        st.rerun()


st.title("Kiniela Predictor")
st.caption("Equipo 2 · clasificación del tipo de resultado de un partido en 6 clases")

try:
    predictor = get_predictor()
except (FileNotFoundError, TypeError) as error:
    st.error(f"No se ha podido cargar el modelo: {error}")
    st.stop()

if is_reference_model(predictor):
    st.warning(
        "**Modelo de prueba.** Todavía no hay un modelo entrenado: la app devuelve el reparto "
        "de clases observado en la Premier League, igual para cualquier partido. "
        "Sirve para probar la app de punta a punta."
    )

teams = get_teams()
st.button("Usar un partido de ejemplo", on_click=use_example_match, args=(teams,))

with st.form("match_form"):
    home_col, away_col = st.columns(2)
    home_team = home_col.selectbox("Equipo local", teams, index=None, format_func=team_label,
                                   placeholder="Elige el equipo local", key="home_team")
    away_team = away_col.selectbox("Equipo visitante", teams, index=None, format_func=team_label,
                                   placeholder="Elige el equipo visitante", key="away_team")
    submitted = st.form_submit_button("Predecir", type="primary", width="stretch")

if submitted:
    run_prediction(home_team, away_team)

if "last_prediction" in st.session_state:
    show_result(st.session_state["last_prediction"])
    show_feedback_form(st.session_state["last_prediction"])

st.caption(f"Modelo: `{predictor.version}`")
