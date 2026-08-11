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
    add_saved_count,
    apply_common_filters,
    load_papers,
    render_paper_list,
)


st.set_page_config(page_title="Team Favorites", page_icon="⭐", layout="wide")

if apply_global_style:
    apply_global_style()

st.title("⭐ Team favorites")
st.write("Papers saved by at least one person on the team.")

df = load_papers()
df = add_saved_count(df)
df = df[df["saved_count"] > 0].copy()

if "published_date" in df.columns:
    df = df.sort_values(["saved_count", "published_date"], ascending=[False, False])
else:
    df = df.sort_values(["saved_count"], ascending=[False])

df = apply_common_filters(df, key_prefix="team_favorites", include_saved_filter=False)

for label, min_count in [
    ("Saved by 3+ people", 3),
    ("Saved by 2 people", 2),
    ("Saved by 1 person", 1),
]:
    if min_count == 1:
        section = df[df["saved_count"] == 1].copy()
    elif min_count == 2:
        section = df[df["saved_count"] == 2].copy()
    else:
        section = df[df["saved_count"] >= 3].copy()

    with st.expander(f"{label} ({len(section):,})", expanded=min_count >= 2):
        render_paper_list(
            section,
            key_prefix=f"team_{min_count}",
            max_cards=60,
            show_save_box=True,
            show_all_notes=True,
        )
