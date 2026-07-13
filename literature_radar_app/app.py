from __future__ import annotations

import sqlite3
from pathlib import Path

import streamlit as st

from src.config import DB_PATH

try:
    from src.ui import apply_global_style
except Exception:
    apply_global_style = None


st.set_page_config(
    page_title="Literature Radar",
    page_icon="📚",
    layout="wide",
)

if apply_global_style:
    apply_global_style()


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

    return {
        "papers": total,
        "with_abstract": with_abstract,
        "saved": saved,
        "latest_update": latest_update,
    }


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

st.markdown("### Main sections")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("**Research topics**")
    st.write("Preventive care")
    st.write("Hypertension")
    st.write("Mental models in health")

with c2:
    st.markdown("**Journal families**")
    st.write("Econ journals")
    st.write("Health journals")
    st.write("General science journals")

with c3:
    st.markdown("**Team reading**")
    st.write("Personal lists")
    st.write("Team favorites")
    st.write("Recent papers")

st.markdown("### Journal coverage")

with st.expander("Econ and development journals", expanded=False):
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
"""
    )

with st.expander("Health economics journals", expanded=False):
    st.markdown(
        """
- Journal of Health Economics
- Health Economics
- American Journal of Health Economics
- European Journal of Health Economics
"""
    )

with st.expander("Medical and global health journals", expanded=False):
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

with st.expander("General science and interdisciplinary journals", expanded=False):
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

st.info(
    "Use the pages in the sidebar to browse papers. Personal notes and saved lists are stored in papers.db."
)
