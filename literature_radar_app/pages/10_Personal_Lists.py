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
    KEEP_COLUMNS,
    PEOPLE,
    apply_common_filters,
    load_papers,
    render_paper_list,
)


st.set_page_config(page_title="Personal Lists", page_icon="👤", layout="wide")

if apply_global_style:
    apply_global_style()

st.title("👤 Personal lists")
st.write("Each person can keep their own reading list and write personal notes.")

person = st.selectbox("Choose person", list(PEOPLE.keys()))
keep_col = KEEP_COLUMNS[person]

df = load_papers()

tab_saved, tab_add = st.tabs([f"{person}'s saved papers", "Find and add papers"])

with tab_saved:
    saved = df[df[keep_col].fillna(0).astype(int) == 1].copy()

    saved = apply_common_filters(
        saved,
        key_prefix=f"personal_saved_{PEOPLE[person]}",
        include_saved_filter=False,
    )

    render_paper_list(
        saved,
        key_prefix=f"personal_saved_cards_{PEOPLE[person]}",
        max_cards=80,
        show_save_box=True,
        show_all_notes=True,
    )

with tab_add:
    st.info("Search papers below, then open the save box on a card to add it to a personal list.")

    browse = apply_common_filters(
        df,
        key_prefix=f"personal_add_{PEOPLE[person]}",
        include_saved_filter=True,
    )

    render_paper_list(
        browse,
        key_prefix=f"personal_add_cards_{PEOPLE[person]}",
        max_cards=80,
        show_save_box=True,
        show_all_notes=True,
    )
