from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.nav_pages import (
    ECON_JOURNALS,
    GENERAL_SCIENCE_JOURNALS,
    HEALTH_JOURNALS,
    render_home_page,
    render_recent_journal_group_page,
    render_topic_page,
)


ROOT = Path(__file__).resolve().parent


st.set_page_config(
    page_title="Literature Radar",
    page_icon="📚",
    layout="wide",
)


try:
    from src.ui import apply_global_style
except Exception:
    apply_global_style = None

if apply_global_style:
    apply_global_style()


def journal_page(path: str) -> str:
    return str(ROOT / path)


def strongly_connected_page() -> None:
    render_topic_page(
        title="Strongly Connected",
        score_col="score_strong",
        subtitle="Papers that look most directly connected to the group's interests.",
        key_prefix="strongly_connected_grouped",
    )


def preventive_care_page() -> None:
    render_topic_page(
        title="Preventive Care",
        score_col="score_preventive",
        subtitle="Papers related to prevention, screening, diagnosis, primary care, and health-seeking behaviour.",
        key_prefix="preventive_care_grouped",
    )


def mental_models_page() -> None:
    render_topic_page(
        title="Mental Models Health",
        score_col="score_mental_models",
        subtitle="Papers related to beliefs, misconceptions, mental models, information, and health behaviour.",
        key_prefix="mental_models_grouped",
    )


def team_health_journals_page() -> None:
    render_recent_journal_group_page(
        title="Health Journal — last 60 days",
        journal_names=HEALTH_JOURNALS,
        key_prefix="team_health_recent_60",
        days=60,
    )


def team_econ_journals_page() -> None:
    render_recent_journal_group_page(
        title="Econ Journal — last 60 days",
        journal_names=ECON_JOURNALS,
        key_prefix="team_econ_recent_60",
        days=60,
    )


def team_general_science_journals_page() -> None:
    render_recent_journal_group_page(
        title="General Science Journal — last 60 days",
        journal_names=GENERAL_SCIENCE_JOURNALS,
        key_prefix="team_science_recent_60",
        days=60,
    )


def hypertension_page() -> None:
    render_topic_page(
        title="Hypertension",
        score_col="score_hypertension",
        subtitle="Papers related to hypertension, blood pressure, screening, diagnosis, treatment, and adherence.",
        key_prefix="hypertension_grouped",
    )


pages = {
    "Home": [
        st.Page(render_home_page, title="Home", icon="🏠", default=True),
    ],
    "Team's interest": [
        st.Page(strongly_connected_page, title="Strongly Connected", icon="⭐"),
        st.Page(preventive_care_page, title="Preventive Care", icon="🩺"),
        st.Page(mental_models_page, title="Mental Models Health", icon="🧠"),
        st.Page(hypertension_page, title="Hypertension", icon="❤️"),
        st.Page(team_health_journals_page, title="Health Journal", icon="🏥"),
        st.Page(team_econ_journals_page, title="Econ Journal", icon="📈"),
        st.Page(team_general_science_journals_page, title="General Science Journal", icon="🔬"),
    ],
    "Work Area": [
        st.Page(journal_page("pages/09_Team_Favorites.py"), title="Team Favorites", icon="⭐"),
        st.Page(journal_page("pages/10_Personal_Lists.py"), title="Personal Lists", icon="👤"),
    ],
}


pg = st.navigation(pages)
pg.run()
