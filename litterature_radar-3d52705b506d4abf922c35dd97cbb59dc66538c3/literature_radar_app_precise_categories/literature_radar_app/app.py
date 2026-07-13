from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import streamlit as st

from src.database import count_papers, get_latest_update, init_db
from src.ui import apply_global_style, hero, soft_note


st.set_page_config(page_title="Literature Radar", layout="wide")
apply_global_style()

hero(
    "Literature Radar",
    "A simple dashboard to track new papers relevant to our research group.",
    "TUM · Behavioral Sciences in Prevention and Care",
)

init_db()

c1, c2 = st.columns(2)
with c1:
    st.metric("Papers in database", count_papers())
with c2:
    st.metric("Last update", get_latest_update() or "Never")

st.markdown("### Pages")

st.page_link("pages/1_Strongly_Connected.py", label="Strongly connected to our work")
st.page_link("pages/2_Econ_Journals_Related.py", label="Econ papers related to our work")
st.page_link("pages/3_Health_Journals_Related.py", label="Health papers related to our work")
st.page_link("pages/4_More_Random_Interesting.py", label="More random but interesting papers")
st.page_link("pages/5_Preventive_Care.py", label="Preventive care")
st.page_link("pages/6_Hypertension.py", label="Hypertension")
st.page_link("pages/7_Mental_Models_Health.py", label="Mental models in health")
st.page_link("pages/8_All_Papers.py", label="All papers")
st.page_link("pages/9_Journal_Groups_and_Rules.py", label="Journal groups and rules")

st.markdown("### Update")

days = st.number_input(
    "Collect papers from the last N days",
    min_value=1,
    max_value=365,
    value=60,
    step=1,
)

if st.button("Run literature update"):
    with st.spinner("Collecting papers..."):
        result = subprocess.run(
            [sys.executable, "scripts/update_papers.py", "--days", str(int(days))],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
        )

    if result.returncode == 0:
        st.success("Update completed.")
        st.rerun()
    else:
        st.error("Update failed.")
        st.code(result.stdout + "\n" + result.stderr)

soft_note("The app collects public metadata and links. It does not download full-text articles.")
