"""Shared resources and formatting for the app pages.

Heavy objects (database engine, model, team list) are created once per server process
with Streamlit's cache, not on every rerun.
"""

from __future__ import annotations

import streamlit as st
from sqlalchemy import Engine

from kiniela.config import CLASS_NAMES
from kiniela.data.catalog import list_teams, load_processed_matches, observed_targets
from kiniela.models.ab_testing import ABRouter, candidate_share, load_candidate
from kiniela.models.predict import Predictor, load_predictor
from kiniela.storage import get_engine, init_db

# Spanish texts for the validation errors raised in src/ (which are in English)
ERROR_MESSAGES = {
    "Both teams are required.": "Elige el equipo local y el visitante.",
    "A team cannot play against itself.": "El equipo local y el visitante no pueden ser el mismo.",
}


@st.cache_resource(show_spinner=False)
def get_db_engine() -> Engine:
    """Database engine (DATABASE_URL, or local SQLite) with the tables created."""
    engine = get_engine()
    init_db(engine)
    return engine


@st.cache_resource(show_spinner="Cargando el modelo…")
def get_predictor() -> Predictor:
    """The promoted model, or the reference model built from the dataset's classes."""
    return load_predictor(reference_targets=observed_targets(load_processed_matches()))


@st.cache_resource(show_spinner=False)
def get_router() -> ABRouter:
    """Chooses the model of each prediction: current, or candidate during an A/B test (#37)."""
    return ABRouter(get_predictor(), load_candidate(), candidate_share())


@st.cache_data(show_spinner=False)
def get_teams() -> list[str]:
    """Teams available in the selectors."""
    return list_teams(load_processed_matches())


def is_reference_model(predictor: Predictor) -> bool:
    return bool(getattr(predictor, "is_reference", False))


def team_label(team: str) -> str:
    """'man city' -> 'Man City'."""
    return team.title()


def class_label(class_id: int) -> str:
    """'1 · Victoria local ajustada'."""
    return f"{class_id} · {CLASS_NAMES[class_id]}"


def user_message(error: Exception) -> str:
    """A readable Spanish message for a validation error."""
    return ERROR_MESSAGES.get(str(error), f"Entrada no válida: {error}")
