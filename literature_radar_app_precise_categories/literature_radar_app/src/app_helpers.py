from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import streamlit as st

from .config import DATA_DIR, load_ranking_rules
from .database import init_db, load_papers, update_review_status, update_feedback_bulk
from .ui import apply_global_style, page_intro


GROUP_LABELS = {
    "broad_science": "Nature / Science / PNAS",
    "medical_broad_science": "Nature Medicine / STM",
    "health_econ_journals": "Health economics journal",
    "top_econ_journals": "Top economics journal",
    "applied_development_econ": "Applied/development econ journal",
    "medical_global_health": "Medical/global health journal",
    # backward compatibility with older collected databases
    "nature_science_pnas": "Nature / Science / PNAS",
    "econ_top": "Top economics journal",
    "econ_field": "Economics field journal",
    "medical_global": "Medical/global health journal",
    "general_science": "General science journal",
}


def _clean_url(value) -> str:
    if value is None:
        return ""
    value = str(value).strip()
    if not value or value.lower() in {"nan", "none", "null"}:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        return value
    if value.startswith("www."):
        return "https://" + value
    return value


def _best_link(row) -> str:
    url = _clean_url(row.get("url", ""))
    doi = str(row.get("doi", "") or "").strip()

    if url:
        return url
    if doi and doi.lower() not in {"nan", "none", "null"}:
        doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
        return f"https://doi.org/{doi}"
    return ""


def _bibtex_escape(value) -> str:
    value = "" if value is None else str(value)
    value = value.replace("\\", "\\\\")
    value = value.replace("{", "\\{").replace("}", "\\}")
    return value.strip()


def _bibtex_key(row) -> str:
    authors = str(row.get("authors", "") or "")
    title = str(row.get("title", "") or "")
    year = str(row.get("published_date", "") or "")[:4]

    first_author = "paper"
    if authors:
        first_author = authors.split(",")[0].strip().split(" ")[-1]
    first_author = re.sub(r"[^A-Za-z0-9]", "", first_author) or "paper"

    title_word = "article"
    for word in re.findall(r"[A-Za-z]{4,}", title):
        if word.lower() not in {"with", "from", "that", "this", "using", "among", "paper", "study"}:
            title_word = word
            break

    return f"{first_author}{year}{title_word}"


def _format_bibtex_authors(authors) -> str:
    authors = str(authors or "").strip()
    if not authors:
        return ""
    parts = [a.strip() for a in authors.split(",") if a.strip()]
    if "et al." in authors.lower():
        parts = [p for p in parts if p.lower() != "et al."]
    return " and ".join(parts) if parts else authors


def _make_bibtex(row) -> str:
    title = _bibtex_escape(row.get("title", ""))
    journal = _bibtex_escape(row.get("journal", ""))
    authors = _bibtex_escape(_format_bibtex_authors(row.get("authors", "")))
    date = str(row.get("published_date", "") or "")
    year = date[:4] if len(date) >= 4 else ""
    doi = str(row.get("doi", "") or "").strip()
    url = _best_link(row)

    lines = [f"@article{{{_bibtex_key(row)},"]

    if title:
        lines.append(f"  title = {{{title}}},")
    if authors:
        lines.append(f"  author = {{{authors}}},")
    if journal:
        lines.append(f"  journal = {{{journal}}},")
    if year:
        lines.append(f"  year = {{{year}}},")
    if doi and doi.lower() not in {"nan", "none", "null"}:
        lines.append(f"  doi = {{{_bibtex_escape(doi)}}},")
    if url:
        lines.append(f"  url = {{{_bibtex_escape(url)}}},")

    if len(lines) > 1 and lines[-1].endswith(","):
        lines[-1] = lines[-1][:-1]

    lines.append("}")
    return "\n".join(lines)


def _short_text(value, max_chars: int = 800) -> str:
    value = "" if value is None else str(value).strip()
    if len(value) <= max_chars:
        return value
    return value[:max_chars].rstrip() + "..."


def filters(prefix: str, default_days: int | None = 90):
    st.markdown("### Filters")
    c1, c2, c3, c4 = st.columns([1, 1, 1.35, 0.9])
    with c1:
        choices = [30, 60, 90, 180, 365, None]
        index = choices.index(default_days) if default_days in choices else 2
        days = st.selectbox(
            "Time window",
            choices,
            index=index,
            format_func=lambda x: "All time" if x is None else f"Last {x} days",
            key=f"{prefix}_days",
        )
    with c2:
        status = st.selectbox("Status", ["All", "new", "interesting", "not relevant", "read"], key=f"{prefix}_status")
    with c3:
        search = st.text_input("Search title/journal/abstract", key=f"{prefix}_search")
    with c4:
        limit = st.number_input("Max rows", min_value=100, max_value=1000, value=100, step=50, key=f"{prefix}_limit")
    return days, status, search, int(limit)


def _prepare_df(df: pd.DataFrame, score_col: str) -> pd.DataFrame:
    df = df.copy()
    df["score"] = df[score_col] if score_col in df.columns else df.get("score_strong", 0)
    df["venue_group"] = df["journal_group"].map(GROUP_LABELS).fillna(df["journal_group"])
    df["link"] = df.apply(_best_link, axis=1)
    df["bibtex"] = df.apply(_make_bibtex, axis=1)
    return df


def _open_selector(df, page_key: str) -> None:
    link_df = df.copy()
    link_df["open_link"] = link_df.apply(_best_link, axis=1)
    link_df = link_df[link_df["open_link"].astype(str).str.len() > 0]

    if link_df.empty:
        return

    st.markdown("### Open paper")
    options = {}
    for _, row in link_df.head(200).iterrows():
        label = f"{str(row['title'])[:100]} — {row.get('journal', '')}"
        options[label] = row["open_link"]

    selected = st.selectbox("Choose a paper", list(options.keys()), key=f"{page_key}_open_select")
    st.link_button("Open selected paper", options[selected])


def _render_paper_cards(df, page_key: str) -> None:
    if df.empty:
        return

    st.markdown("### Readable view")
    st.caption("This view avoids horizontal scrolling. Use the compact feedback table below to save ticks.")

    n_cards = st.slider(
        "Number of papers to show as cards",
        min_value=10,
        max_value=max(10, min(100, len(df))),
        value=min(25, len(df)),
        step=5,
        key=f"{page_key}_n_cards",
    )

    for i, (_, row) in enumerate(df.head(n_cards).iterrows(), start=1):
        score = row.get("score", "")
        title = str(row.get("title", "") or "Untitled")
        journal = str(row.get("journal", "") or "")
        venue_group = str(row.get("venue_group", "") or "")
        date = str(row.get("published_date", "") or "")
        authors = str(row.get("authors", "") or "")
        abstract = _short_text(row.get("abstract", ""), 800)
        url = _best_link(row)
        bibtex = _make_bibtex(row)

        with st.container(border=True):
            top_left, top_right = st.columns([5, 1])
            with top_left:
                st.markdown(f"**{i}. {title}**")
                st.caption(f"{journal} · {venue_group} · {date} · Relevance score: {score}")
                if authors:
                    st.caption(authors)
            with top_right:
                if url:
                    st.link_button("Open", url, use_container_width=True)

            if abstract:
                st.write(abstract)
            else:
                st.caption("No abstract available in the metadata source.")

            with st.expander("BibTeX"):
                st.code(bibtex, language="bibtex")


def _render_feedback_table(df, page_key: str) -> None:
    people = {
        "Nikkil": "feedback_nikkil",
        "Anna": "feedback_anna",
        "Caterina": "feedback_caterina",
        "Michaela": "feedback_michaela",
        "Vasanthi": "feedback_vasanthi",
    }

    feedback_df = df.copy()
    for display_name, col in people.items():
        if col not in feedback_df.columns:
            feedback_df[col] = 0
        feedback_df[display_name] = feedback_df[col].fillna(0).astype(int).astype(bool)

    feedback_df["paper"] = feedback_df["title"].astype(str).str.slice(0, 95)

    show = feedback_df[
        [
            "unique_key",
            "score",
            "paper",
            "journal",
            "Nikkil",
            "Anna",
            "Caterina",
            "Michaela",
            "Vasanthi",
        ]
    ]

    st.markdown("### Team feedback")
    st.caption("This compact table is only for ticks, so it should fit on screen without horizontal scrolling.")

    edited = st.data_editor(
        show,
        use_container_width=True,
        hide_index=True,
        disabled=["unique_key", "score", "paper", "journal"],
        column_config={
            "unique_key": None,
            "score": st.column_config.NumberColumn("Score", width="small"),
            "paper": st.column_config.TextColumn("Paper", width="large"),
            "journal": st.column_config.TextColumn("Journal", width="medium"),
            "Nikkil": st.column_config.CheckboxColumn("Nikkil", width="small"),
            "Anna": st.column_config.CheckboxColumn("Anna", width="small"),
            "Caterina": st.column_config.CheckboxColumn("Caterina", width="small"),
            "Michaela": st.column_config.CheckboxColumn("Michaela", width="small"),
            "Vasanthi": st.column_config.CheckboxColumn("Vasanthi", width="small"),
        },
        key=f"{page_key}_compact_feedback_editor",
    )

    if st.button("Save checkboxes", key=f"{page_key}_save_compact_feedback"):
        feedback_rows = []
        for _, row in edited.iterrows():
            feedback_rows.append(
                {
                    "unique_key": row["unique_key"],
                    "feedback_nikkil": bool(row["Nikkil"]),
                    "feedback_anna": bool(row["Anna"]),
                    "feedback_caterina": bool(row["Caterina"]),
                    "feedback_michaela": bool(row["Michaela"]),
                    "feedback_vasanthi": bool(row["Vasanthi"]),
                }
            )
        update_feedback_bulk(feedback_rows)
        st.success("Checkboxes saved.")
        st.rerun()


def _render_bibtex_table(df, page_key: str) -> None:
    st.markdown("### BibTeX table")
    st.caption("Ready-to-copy BibTeX entries for the selected papers.")

    show = df[["title", "journal", "published_date", "bibtex"]]

    st.dataframe(
        show,
        use_container_width=True,
        hide_index=True,
        column_config={
            "title": st.column_config.TextColumn("Title", width="large"),
            "journal": st.column_config.TextColumn("Journal", width="medium"),
            "published_date": st.column_config.TextColumn("Date", width="small"),
            "bibtex": st.column_config.TextColumn("BibTeX", width="large"),
        },
    )


def _render_review_status(df, page_key: str) -> None:
    if df.empty:
        return

    st.markdown("### Review status")
    options = {f"{row['title'][:90]} — {row['journal']}": row["unique_key"] for _, row in df.head(100).iterrows()}
    selected = st.selectbox("Paper", list(options.keys()), key=f"{page_key}_paper_select")
    c1, c2 = st.columns([1, 2])
    with c1:
        new_status = st.selectbox("New status", ["new", "interesting", "not relevant", "read"], key=f"{page_key}_new_status")
    with c2:
        notes = st.text_input("Notes", key=f"{page_key}_notes")

    if st.button("Save status", key=f"{page_key}_save"):
        update_review_status(options[selected], new_status, notes)
        st.success("Saved.")
        st.rerun()


def _render_compact_table(df, page_key: str, all_scores: bool = False) -> None:
    if all_scores:
        compact = df[
            [
                "published_date",
                "venue_group",
                "journal",
                "title",
                "abstract",
                "score_strong",
                "score_econ",
                "score_health",
                "score_random",
                "link",
                "bibtex",
            ]
        ]
    else:
        compact = df[
            [
                "score",
                "published_date",
                "venue_group",
                "journal",
                "title",
                "abstract",
                "link",
                "bibtex",
            ]
        ].rename(columns={"published_date": "date"})

    st.markdown("### Compact table")
    st.caption("Fewer columns than before, with abstract and BibTeX included.")

    st.dataframe(
        compact,
        use_container_width=True,
        hide_index=True,
        column_config={
            "score": st.column_config.NumberColumn("Score", width="small"),
            "date": st.column_config.TextColumn("Date", width="small"),
            "published_date": st.column_config.TextColumn("Date", width="small"),
            "venue_group": st.column_config.TextColumn("Venue group", width="medium"),
            "journal": st.column_config.TextColumn("Journal", width="medium"),
            "title": st.column_config.TextColumn("Title", width="large"),
            "abstract": st.column_config.TextColumn("Abstract", width="large"),
            "score_strong": st.column_config.NumberColumn("Strong", width="small"),
            "score_econ": st.column_config.NumberColumn("Econ", width="small"),
            "score_health": st.column_config.NumberColumn("Health", width="small"),
            "score_random": st.column_config.NumberColumn("Adjacent", width="small"),
            "link": st.column_config.LinkColumn("Link", width="medium"),
            "bibtex": st.column_config.TextColumn("BibTeX", width="large"),
        },
    )


def _render_page_body(df: pd.DataFrame, page_key: str):
    sort_label = st.selectbox(
        "Sort by",
        ["Relevance score", "Publication date", "Journal"],
        key=f"{page_key}_sort",
    )
    if sort_label == "Relevance score":
        df = df.sort_values(["score", "published_date"], ascending=[False, False])
    elif sort_label == "Publication date":
        df = df.sort_values("published_date", ascending=False)
    else:
        df = df.sort_values(["journal", "published_date"], ascending=[True, False])

    view = st.radio(
        "Display mode",
        ["Readable cards", "Compact table", "BibTeX table"],
        horizontal=True,
        key=f"{page_key}_display_mode",
    )

    if view == "Readable cards":
        _render_paper_cards(df, page_key)
        _render_feedback_table(df, page_key)
    elif view == "Compact table":
        _render_compact_table(df, page_key)
        _render_feedback_table(df, page_key)
    else:
        _render_bibtex_table(df, page_key)

    _open_selector(df, page_key)
    _render_review_status(df, page_key)


def render_interest_page(
    page_key: str,
    title: str,
    description: str,
    score_col: str,
    min_score_key: str,
    allowed_journal_groups: list[str] | None = None,
    pills: list[tuple[str, str]] | None = None,
    default_min_override: int | None = None,
    default_days: int | None = 90,
):
    st.set_page_config(page_title=title, layout="wide")
    apply_global_style()
    page_intro(title, description, pills or [])

    init_db()
    rules = load_ranking_rules()
    settings = rules.get("settings", {})
    default_min = int(settings.get(min_score_key, settings.get("default_min_score", 20)))
    if default_min_override is not None:
        default_min = int(default_min_override)

    days, status, search, limit = filters(page_key, default_days=default_days)
    min_score = st.slider("Minimum relevance score", 0, 120, default_min, 1)

    df = load_papers(score_col=score_col, min_score=min_score, days=days, search=search, status=status, limit=limit)

    if df.empty:
        st.info("No papers found yet. Run an update from the home page or lower the minimum score.")
        return

    if allowed_journal_groups:
        backward_map = {
            "top_econ_journals": ["econ_top"],
            "health_econ_journals": ["econ_field"],
            "applied_development_econ": ["econ_field"],
            "medical_global_health": ["medical_global"],
            "medical_broad_science": [],
            "broad_science": ["general_science", "nature_science_pnas"],
        }
        expanded = set(allowed_journal_groups)
        for g in allowed_journal_groups:
            expanded.update(backward_map.get(g, []))
        df = df[df["journal_group"].isin(expanded)].copy()

    if df.empty:
        st.info("No papers found in this journal group. Try a longer time window, lower the score, or run a new update.")
        return

    df = _prepare_df(df, score_col=score_col)

    if allowed_journal_groups:
        st.metric("Papers in this interest category and journal group", len(df))
    else:
        st.metric("Papers in this interest category", len(df))

    _render_page_body(df, page_key)


def render_all_papers_page():
    st.set_page_config(page_title="All papers", layout="wide")
    apply_global_style()
    page_intro(
        "All papers",
        "All collected papers, regardless of interest category or journal group. Use this page to search the full database.",
        [("complete database", "blue"), ("searchable", "green")]
    )

    init_db()
    days, status, search, limit = filters("all")
    df = load_papers(score_col=None, days=days, search=search, status=status, limit=limit)

    if df.empty:
        st.info("No papers found yet. Run an update from the home page.")
        return

    df = _prepare_df(df, score_col="score_strong")

    view = st.radio(
        "Display mode",
        ["Readable cards", "Compact table", "BibTeX table"],
        horizontal=True,
        key="all_display_mode",
    )

    if view == "Readable cards":
        _render_paper_cards(df, "all")
    elif view == "Compact table":
        _render_compact_table(df, "all", all_scores=True)
    else:
        _render_bibtex_table(df, "all")

    _open_selector(df, "all")


def render_rules_page():
    st.set_page_config(page_title="Journal groups and ranking rules", layout="wide")
    apply_global_style()
    page_intro(
        "Journal groups and ranking rules",
        "Interest categories are scored by keywords, but Econ and Health pages are restricted to the correct publication venues.",
        [("interest categories", "blue"), ("journal groups", "green"), ("YAML", "purple")]
    )

    st.subheader("journals.yml")
    st.code((DATA_DIR / "journals.yml").read_text(encoding="utf-8"), language="yaml")

    st.subheader("ranking_rules.yml")
    st.code((DATA_DIR / "ranking_rules.yml").read_text(encoding="utf-8"), language="yaml")


# backward-compatible name, in case old pages still import it
def render_ranked_page(page_key: str, title: str, description: str, score_col: str, reason_col: str, min_score_key: str):
    render_interest_page(
        page_key=page_key,
        title=title,
        description=description,
        score_col=score_col,
        min_score_key=min_score_key,
        allowed_journal_groups=None,
    )
