from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import streamlit as st

from src.database import count_papers, get_latest_update, init_db
from src.ui import apply_global_style, card, hero, soft_note


st.set_page_config(page_title="Literature Radar", layout="wide")
apply_global_style()

hero(
    "Literature Radar",
    "Interest-based rankings for Nikkil Sudharsanan's group, with Econ and Health pages restricted to the correct publication venues.",
    "TUM · Behavioral science for disease prevention and health care",
)

init_db()

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Papers in database", count_papers())
with c2:
    st.metric("Last update", get_latest_update() or "Never")
with c3:
    st.metric("Update rhythm", "1st + 15th")

st.markdown("### Interest categories")

r1c1, r1c2 = st.columns(2)
with r1c1:
    card(
        "Strongly connected to Nikkil's group",
        "All selected journals. Ranked by fit with the group: preventive care, health behavior, hypertension, adherence, LMICs, aging, demography, and interventions.",
        [("all journals", "blue"), ("highest priority", "green")],
    )
    st.page_link("pages/1_Strongly_Connected.py", label="Open strongly connected page")

with r1c2:
    card(
        "Econ papers related to our work",
        "Interest ranking, but only among Econ publication venues: health economics, top economics, applied economics, and development economics journals.",
        [("econ journals only", "blue"), ("health/development econ", "orange")],
    )
    st.page_link("pages/2_Econ_Journals_Related.py", label="Open Econ page")

r2c1, r2c2 = st.columns(2)
with r2c1:
    card(
        "Health papers related to our work",
        "Interest ranking, but only among Health/medical venues: JAMA, BMJ, Lancet, NEJM, PLOS Medicine, Nature Medicine, and Science Translational Medicine.",
        [("health journals only", "green"), ("global health", "blue")],
    )
    st.page_link("pages/3_Health_Journals_Related.py", label="Open Health page")

with r2c2:
    card(
        "More random but interesting papers",
        "Adjacent-interest papers mainly from broad science venues: Nature, Science, Science Advances, Nature Human Behaviour, and PNAS.",
        [("broad science", "purple"), ("adjacent ideas", "blue")],
    )
    st.page_link("pages/4_More_Random_Interesting.py", label="Open adjacent page")

st.markdown("### Precise categories")

p1, p2, p3 = st.columns(3)
with p1:
    card(
        "Preventive care",
        "Across all selected journals: preventive care, screening, early detection, primary care, follow-up, CHWs, and health services.",
        [("all journals", "blue"), ("prevention", "green")]
    )
    st.page_link("pages/5_Preventive_Care.py", label="Open preventive care")

with p2:
    card(
        "Hypertension",
        "Across all selected journals: hypertension, blood pressure, CVD, NCDs, screening, treatment, adherence, and care cascades.",
        [("all journals", "blue"), ("hypertension", "green")]
    )
    st.page_link("pages/6_Hypertension.py", label="Open hypertension")

with p3:
    card(
        "Mental models in health",
        "Across all selected journals: beliefs, belief change, misinformation, risk perception, behavior change, trust, and health communication.",
        [("all journals", "blue"), ("beliefs", "purple")]
    )
    st.page_link("pages/7_Mental_Models_Health.py", label="Open mental models")

st.markdown("### Database and settings")
d1, d2 = st.columns(2)
with d1:
    card(
        "All papers",
        "Search the full database, regardless of interest category or journal group.",
        [("full database", "blue")],
    )
    st.page_link("pages/8_All_Papers.py", label="Open all papers")
with d2:
    card(
        "Journal groups and ranking rules",
        "Inspect the journal grouping and the keyword rules used to score interests.",
        [("journal groups", "green"), ("rules", "purple")],
    )
    st.page_link("pages/9_Journal_Groups_and_Rules.py", label="Open journal groups and rules")

st.markdown("### Update now")
u1, u2 = st.columns([1, 2])
with u1:
    days = st.number_input(
        "Collect papers from the last N days",
        min_value=1,
        max_value=365,
        value=60,
        step=1,
    )
with u2:
    soft_note(
        "For the first update, 60 days helps fill the database quickly. For Econ journals, use update_econ_papers.bat once to collect a 365-day window, because Econ journals publish fewer relevant papers."
    )

if st.button("Run literature update"):
    with st.spinner("Collecting papers. This can take a few minutes for all journals."):
        result = subprocess.run(
            [sys.executable, "scripts/update_papers.py", "--days", str(int(days))],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
        )
    if result.returncode == 0:
        st.success("Update completed.")
        st.code(result.stdout[-4000:])
        st.rerun()
    else:
        st.error("Update failed.")
        st.code(result.stdout + "\n" + result.stderr)

st.markdown("### Econ journal update")
soft_note(
    "To get more Econ papers, close the app and double-click update_econ_papers.bat once. It collects one year of papers only from Econ journals, then the Econ page will rank them."
)

soft_note("The app only collects public metadata and links. It does not download paywalled articles.")
