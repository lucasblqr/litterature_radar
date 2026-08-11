from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from src.personal_lists import (
    apply_common_filters,
    filter_by_journals,
    load_papers,
    render_paper_list,
)


def render_single_journal_page(
    title: str,
    journal_names: list[str],
    key_prefix: str,
) -> None:
    st.title(title)

    df = load_papers()
    df = filter_by_journals(df, journal_names)

    if "published_date" in df.columns:
        df = df.sort_values("published_date", ascending=False)

    df = apply_common_filters(df, key_prefix=key_prefix)

    render_paper_list(
        df,
        key_prefix=f"{key_prefix}_cards",
        max_cards=100,
        show_save_box=True,
        show_all_notes=True,
    )


def safe_key(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
