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
    "Health Journal": [
        st.Page(journal_page("pages/journals/bmj_global_health.py"), title="BMJ Global Health"),
        st.Page(journal_page("pages/journals/the_lancet_global_health.py"), title="The Lancet Global Health"),
        st.Page(journal_page("pages/journals/plos_medicine.py"), title="PLOS Medicine"),
        st.Page(journal_page("pages/journals/social_science_medicine.py"), title="Social Science & Medicine"),
        st.Page(journal_page("pages/journals/jama.py"), title="JAMA"),
        st.Page(journal_page("pages/journals/jama_network_open.py"), title="JAMA Network Open"),
        st.Page(journal_page("pages/journals/bmj.py"), title="BMJ"),
        st.Page(journal_page("pages/journals/the_lancet.py"), title="The Lancet"),
        st.Page(journal_page("pages/journals/new_england_journal_of_medicine.py"), title="New England Journal of Medicine"),
        st.Page(journal_page("pages/journals/nature_medicine.py"), title="Nature Medicine"),
    ],
    "General Science Journals": [
        st.Page(journal_page("pages/journals/nature.py"), title="Nature"),
        st.Page(journal_page("pages/journals/nature_human_behaviour.py"), title="Nature Human Behaviour"),
        st.Page(journal_page("pages/journals/science.py"), title="Science"),
        st.Page(journal_page("pages/journals/science_advances.py"), title="Science Advances"),
        st.Page(journal_page("pages/journals/science_translational_medicine.py"), title="Science Translational Medicine"),
        st.Page(journal_page("pages/journals/pnas.py"), title="PNAS"),
    ],
    "Economics Journal": [
        st.Page(journal_page("pages/journals/american_economic_review.py"), title="American Economic Review"),
        st.Page(journal_page("pages/journals/quarterly_journal_of_economics.py"), title="Quarterly Journal of Economics"),
        st.Page(journal_page("pages/journals/journal_of_political_economy.py"), title="Journal of Political Economy"),
        st.Page(journal_page("pages/journals/econometrica.py"), title="Econometrica"),
        st.Page(journal_page("pages/journals/review_of_economics_and_statistics.py"), title="Review of Economics and Statistics"),
        st.Page(journal_page("pages/journals/aej_applied_economics.py"), title="AEJ: Applied Economics"),
        st.Page(journal_page("pages/journals/aer_insights.py"), title="AER Insights"),
        st.Page(journal_page("pages/journals/journal_of_development_economics.py"), title="Journal of Development Economics"),
        st.Page(journal_page("pages/journals/journal_of_health_economics.py"), title="Journal of Health Economics"),
        st.Page(journal_page("pages/journals/health_economics.py"), title="Health Economics"),
        st.Page(journal_page("pages/journals/american_journal_of_health_economics.py"), title="American Journal of Health Economics"),
        st.Page(journal_page("pages/journals/european_journal_of_health_economics.py"), title="European Journal of Health Economics"),
    ],
    "Work Area": [
        st.Page(journal_page("pages/09_Team_Favorites.py"), title="Team Favorites", icon="⭐"),
        st.Page(journal_page("pages/10_Personal_Lists.py"), title="Personal Lists", icon="👤"),
    ],
}


pg = st.navigation(pages)
pg.run()
