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


st.set_page_config(page_title="General Science Journals", page_icon="🔬", layout="wide")

if apply_global_style:
    apply_global_style()


GROUPS = {
    "General science": [
        "Nature",
        "Science",
        "PNAS",
        "Proceedings of the National Academy of Sciences",
    ],
    "Interdisciplinary and behavioural science": [
        "Nature Human Behaviour",
        "Nature Human Behavior",
        "Science Advances",
        "Science Translational Medicine",
    ],
}

render_journal_family_page("🔬 General science journals", GROUPS, key_prefix="science_journals")
