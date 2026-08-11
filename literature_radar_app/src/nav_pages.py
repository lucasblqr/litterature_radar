from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import DB_PATH
from src.personal_lists import (
    apply_common_filters,
    load_papers,
    render_paper_list,
)


def read_metrics() -> dict[str, int | str]:
    if not Path(DB_PATH).exists():
        return {
            "papers": 0,
            "with_abstract": 0,
            "saved": 0,
            "latest_update": "Not available",
        }

    with sqlite3.connect(DB_PATH) as conn:
        total = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]

        with_abstract = conn.execute(
            "SELECT COUNT(*) FROM papers WHERE COALESCE(TRIM(abstract), '') != ''"
        ).fetchone()[0]

        cols = [r[1] for r in conn.execute("PRAGMA table_info(papers)").fetchall()]
        keep_cols = [c for c in cols if c.startswith("keep_")]

        saved = 0
        if keep_cols:
            saved_expr = " + ".join([f"COALESCE({c}, 0)" for c in keep_cols])
            saved = conn.execute(
                f"SELECT COUNT(*) FROM papers WHERE ({saved_expr}) > 0"
            ).fetchone()[0]

        latest_update = "Not available"

        if "fetched_at" in cols:
            latest_update = conn.execute(
                "SELECT MAX(fetched_at) FROM papers WHERE COALESCE(TRIM(fetched_at), '') != ''"
            ).fetchone()[0] or "Not available"
        elif "published_date" in cols:
            latest_update = conn.execute(
                "SELECT MAX(published_date) FROM papers WHERE COALESCE(TRIM(published_date), '') != ''"
            ).fetchone()[0] or "Not available"

    return {
        "papers": total,
        "with_abstract": with_abstract,
        "saved": saved,
        "latest_update": latest_update,
    }


# Aggregate journal pages shown inside "Team's interest".  These lists mirror
# the journal sections in app.py, but the aggregate pages intentionally apply
# no topic/ranking/saved/abstract filters: only journal membership and a true
# publication-date window of the last 60 days.
HEALTH_JOURNALS = [
    "BMJ Global Health",
    "The Lancet Global Health",
    "Lancet Global Health",
    "PLOS Medicine",
    "PLoS Medicine",
    "Social Science & Medicine",
    "Social Science and Medicine",
    "JAMA",
    "Journal of the American Medical Association",
    "JAMA Network Open",
    "BMJ",
    "The BMJ",
    "The Lancet",
    "Lancet",
    "New England Journal of Medicine",
    "The New England Journal of Medicine",
    "NEJM",
    "Nature Medicine",
]

ECON_JOURNALS = [
    "American Economic Review",
    "Quarterly Journal of Economics",
    "The Quarterly Journal of Economics",
    "Journal of Political Economy",
    "Econometrica",
    "Review of Economics and Statistics",
    "The Review of Economics and Statistics",
    "American Economic Journal: Applied Economics",
    "AEJ: Applied Economics",
    "AER: Insights",
    "AER Insights",
    "Journal of Development Economics",
    "Journal of Health Economics",
    "Health Economics",
    "American Journal of Health Economics",
    "The European Journal of Health Economics",
    "European Journal of Health Economics",
]

GENERAL_SCIENCE_JOURNALS = [
    "Nature",
    "Nature Human Behaviour",
    "Nature Human Behavior",
    "Science",
    "Science Advances",
    "Science Translational Medicine",
    "PNAS",
    "Proceedings of the National Academy of Sciences",
    "Proceedings of the National Academy of Sciences of the United States of America",
]


def _filter_published_last_n_days(df: pd.DataFrame, days: int) -> pd.DataFrame:
    """Keep papers truly published from today-days through today (inclusive).

    This deliberately uses publication date rather than fetched_at.  It also
    excludes future-dated issue metadata, so "past 60 days" means past 60 days.
    """
    if df.empty or "published_date" not in df.columns:
        return df.iloc[0:0].copy()

    published = pd.to_datetime(df["published_date"], errors="coerce").dt.date
    today = date.today()
    cutoff = today - timedelta(days=int(days))
    mask = published.notna() & (published >= cutoff) & (published <= today)

    out = df[mask].copy()
    out["_published_sort"] = pd.to_datetime(out["published_date"], errors="coerce")
    out = out.sort_values(
        ["_published_sort", "fetched_at"] if "fetched_at" in out.columns else ["_published_sort"],
        ascending=False,
        na_position="last",
    ).drop(columns=["_published_sort"])
    return out


def render_recent_journal_group_page(
    title: str,
    journal_names: list[str],
    key_prefix: str,
    days: int = 60,
) -> None:
    """Render every paper from a journal family published in the last N days.

    No topic score, keyword, abstract, saved-status, or journal UI filter is
    applied.  The only restrictions are the requested journal family and date
    window.
    """
    from src.personal_lists import filter_by_journals

    st.title(title)

    today = date.today()
    cutoff = today - timedelta(days=int(days))
    st.caption(
        f"All papers from these journals published in the past {days} days "
        f"({cutoff.isoformat()} to {today.isoformat()}). No topic or ranking filters are applied."
    )

df = load_papers()
df = filter_by_journals(df, journal_names)
df = _filter_published_last_n_days(df, days)

    render_paper_list(
        df,
        key_prefix=f"{key_prefix}_cards",
        max_cards=max(100, len(df)),
        show_save_box=True,
        show_all_notes=True,
    )


def render_home_page() -> None:
    metrics = read_metrics()

    st.title("📚 Literature Radar")
    st.write(
        "A shared dashboard to find, read, and save papers that may be relevant for our research group."
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Papers in database", f"{metrics['papers']:,}")
    m2.metric("With abstracts", f"{metrics['with_abstract']:,}")
    m3.metric("Saved by team", f"{metrics['saved']:,}")
    m4.metric("Latest update", str(metrics["latest_update"])[:10])

    st.markdown("### Browse by section")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Team's interest**")
        st.write("Strongly Connected")
        st.write("Preventive Care")
        st.write("Mental Models Health")
        st.write("Hypertension")
        st.write("Health Journal — last 60 days")
        st.write("Econ Journal — last 60 days")
        st.write("General Science Journal — last 60 days")

    with c2:
        st.markdown("**Journal groups**")
        st.write("Health Journal")
        st.write("General Science Journals")
        st.write("Economics Journal")

    with c3:
        st.markdown("**Work Area**")
        st.write("Team Favorites")
        st.write("Personal Lists")

    st.markdown("### Journal coverage")

    with st.expander("Health Journal", expanded=False):
        st.markdown(
            """
- BMJ Global Health
- The Lancet Global Health
- PLOS Medicine
- Social Science & Medicine
- JAMA
- JAMA Network Open
- BMJ
- The Lancet
- New England Journal of Medicine
- Nature Medicine
"""
        )

    with st.expander("General Science Journals", expanded=False):
        st.markdown(
            """
- Nature
- Nature Human Behaviour
- Science
- Science Advances
- Science Translational Medicine
- PNAS
"""
        )

    with st.expander("Economics Journal", expanded=False):
        st.markdown(
            """
- American Economic Review
- Quarterly Journal of Economics
- Journal of Political Economy
- Econometrica
- Review of Economics and Statistics
- American Economic Journal: Applied Economics
- AER Insights
- Journal of Development Economics
- Journal of Health Economics
- Health Economics
- American Journal of Health Economics
- European Journal of Health Economics
"""
        )

    st.info(
        "Use the grouped sidebar to browse papers. Personal notes and saved lists are stored in papers.db."
    )


def render_topic_page(
    title: str,
    score_col: str,
    subtitle: str,
    key_prefix: str,
) -> None:
    st.title(title)
    st.write(subtitle)

    df = load_papers()

    if score_col in df.columns:
        df[score_col] = pd.to_numeric(df[score_col], errors="coerce").fillna(0)
        df = df[df[score_col] > 0].copy()

        sort_cols = [score_col]
        ascending = [False]

        if "published_date" in df.columns:
            sort_cols.append("published_date")
            ascending.append(False)

        df = df.sort_values(sort_cols, ascending=ascending)

    df = apply_common_filters(df, key_prefix=key_prefix)

    render_paper_list(
        df,
        key_prefix=f"{key_prefix}_cards",
        max_cards=100,
        show_save_box=True,
        show_all_notes=True,
    )
