from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from src.ui import apply_global_style
except Exception:
    apply_global_style = None

from src.personal_lists import render_journal_family_page


st.set_page_config(page_title="Health Journals", page_icon="🏥", layout="wide")

if apply_global_style:
    apply_global_style()


GROUPS = {
    "Global health and public health": [
        "BMJ Global Health",
        "The Lancet Global Health",
        "Lancet Global Health",
        "PLOS Medicine",
        "Social Science & Medicine",
        "Social Science and Medicine",
    ],
    "General medical journals": [
        "JAMA",
        "JAMA Network Open",
        "BMJ",
        "The Lancet",
        "Lancet",
        "New England Journal of Medicine",
        "NEJM",
        "Nature Medicine",
    ],
    "Health economics": [
        "Journal of Health Economics",
        "Health Economics",
        "American Journal of Health Economics",
        "European Journal of Health Economics",
    ],
}

render_journal_family_page("🏥 Health journals", GROUPS, key_prefix="health_journals")
