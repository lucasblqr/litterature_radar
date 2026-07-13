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

from src.personal_lists import (
    apply_common_filters,
    filter_recent,
    load_papers,
    render_paper_list,
)


st.set_page_config(page_title="Recent Papers", page_icon="🆕", layout="wide")

if apply_global_style:
    apply_global_style()

st.title("🆕 Recent papers")

window = st.radio(
    "Time window",
    ["Last 7 days", "Last 30 days", "Last 90 days"],
    horizontal=True,
)

days = {
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
}[window]

df = load_papers()
df = filter_recent(df, days)
df = apply_common_filters(df, key_prefix=f"recent_{days}")

render_paper_list(
    df,
    key_prefix=f"recent_cards_{days}",
    max_cards=80,
    show_save_box=True,
    show_all_notes=True,
)
