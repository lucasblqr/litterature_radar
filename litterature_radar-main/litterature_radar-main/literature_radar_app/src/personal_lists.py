from __future__ import annotations

import re
import sqlite3
from typing import Iterable

import pandas as pd
import streamlit as st

from src.config import DB_PATH


PEOPLE = {
    "Nikkil": "nikkil",
    "Anna": "anna",
    "Lucas": "lucas",
    "Vasanthi": "vasanthi",
    "Michaela": "michaela",
    "Caterina": "caterina",
}

KEEP_COLUMNS = {name: f"keep_{slug}" for name, slug in PEOPLE.items()}
NOTE_COLUMNS = {name: f"note_{slug}" for name, slug in PEOPLE.items()}


def connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def table_columns(conn: sqlite3.Connection) -> set[str]:
    return {row[1] for row in conn.execute("PRAGMA table_info(papers)").fetchall()}


def ensure_personal_columns() -> None:
    with connect() as conn:
        cols = table_columns(conn)

        for col in KEEP_COLUMNS.values():
            if col not in cols:
                conn.execute(f"ALTER TABLE papers ADD COLUMN {col} INTEGER DEFAULT 0")

        cols = table_columns(conn)

        for col in NOTE_COLUMNS.values():
            if col not in cols:
                conn.execute(f"ALTER TABLE papers ADD COLUMN {col} TEXT DEFAULT ''")

        conn.commit()


def available_columns() -> list[str]:
    with connect() as conn:
        cols = table_columns(conn)

    preferred = [
        "unique_key",
        "title",
        "journal",
        "configured_journal",
        "journal_group",
        "source",
        "doi",
        "url",
        "published_date",
        "authors",
        "abstract",
        "fetched_at",
        "score_strong",
        "score_econ",
        "score_health",
        "score_random",
        "score_preventive",
        "score_hypertension",
        "score_mental_models",
    ]

    personal = list(KEEP_COLUMNS.values()) + list(NOTE_COLUMNS.values())

    return [c for c in preferred + personal if c in cols]


def load_papers(limit: int | None = None) -> pd.DataFrame:
    ensure_personal_columns()

    cols = available_columns()
    col_sql = ", ".join(cols)
    limit_sql = "" if limit is None else f"LIMIT {int(limit)}"

    query = f"""
    SELECT {col_sql}
    FROM papers
    ORDER BY COALESCE(published_date, '') DESC, COALESCE(fetched_at, '') DESC
    {limit_sql}
    """

    with connect() as conn:
        df = pd.read_sql_query(query, conn)

    for col in KEEP_COLUMNS.values():
        if col not in df.columns:
            df[col] = 0

    for col in NOTE_COLUMNS.values():
        if col not in df.columns:
            df[col] = ""

    return df


def update_personal_choice(unique_key: str, person: str, keep: bool, note: str) -> None:
    slug = PEOPLE[person]
    keep_col = f"keep_{slug}"
    note_col = f"note_{slug}"

    ensure_personal_columns()

    with connect() as conn:
        conn.execute(
            f"""
            UPDATE papers
            SET {keep_col} = ?,
                {note_col} = ?
            WHERE unique_key = ?
            """,
            (1 if keep else 0, note or "", unique_key),
        )
        conn.commit()


def text_value(value) -> str:
    if value is None:
        return ""

    if isinstance(value, float) and pd.isna(value):
        return ""

    return str(value)


def short_text(value, n: int = 900) -> str:
    text = re.sub(r"\s+", " ", text_value(value)).strip()

    if len(text) <= n:
        return text

    return text[: n - 1].rstrip() + "…"


def paper_link(row: pd.Series) -> str:
    doi = text_value(row.get("doi", "")).strip()
    url = text_value(row.get("url", "")).strip()

    if doi:
        if doi.startswith("http://") or doi.startswith("https://"):
            return doi

        if doi.startswith("10."):
            return f"https://doi.org/{doi}"

    return url


def saved_by(row: pd.Series) -> list[str]:
    names = []

    for name, col in KEEP_COLUMNS.items():
        try:
            keep = int(row.get(col, 0) or 0)
        except Exception:
            keep = 0

        if keep == 1:
            names.append(name)

    return names


def note_items(row: pd.Series) -> list[tuple[str, str]]:
    out = []

    for name, col in NOTE_COLUMNS.items():
        note = text_value(row.get(col, "")).strip()

        if note:
            out.append((name, note))

    return out


def saved_count(row: pd.Series) -> int:
    return len(saved_by(row))


def add_saved_count(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    if out.empty:
        out["saved_count"] = 0
        return out

    out["saved_count"] = out.apply(saved_count, axis=1)

    return out


def filter_by_journals(df: pd.DataFrame, journal_names: Iterable[str]) -> pd.DataFrame:
    names = [x.lower() for x in journal_names]

    journal = df.get("journal", pd.Series("", index=df.index)).fillna("").str.lower()
    configured = df.get("configured_journal", pd.Series("", index=df.index)).fillna("").str.lower()

    mask = pd.Series(False, index=df.index)

    for name in names:
        mask = mask | journal.str.contains(re.escape(name), na=False)
        mask = mask | configured.str.contains(re.escape(name), na=False)

    return df[mask].copy()


def filter_recent(df: pd.DataFrame, days: int) -> pd.DataFrame:
    out = df.copy()

    if "fetched_at" in out.columns:
        dates = pd.to_datetime(out["fetched_at"], errors="coerce", utc=True)

        if dates.notna().any():
            cutoff = dates.max() - pd.Timedelta(days=days)
            return out[dates >= cutoff].copy()

    if "published_date" in out.columns:
        dates = pd.to_datetime(out["published_date"], errors="coerce", utc=True)

        if dates.notna().any():
            cutoff = dates.max() - pd.Timedelta(days=days)
            return out[dates >= cutoff].copy()

    return out


def apply_common_filters(
    df: pd.DataFrame,
    key_prefix: str,
    include_saved_filter: bool = True,
) -> pd.DataFrame:
    out = df.copy()

    with st.expander("Filters", expanded=True):
        search = st.text_input(
            "Search title, abstract, authors, journal, notes",
            key=f"{key_prefix}_search",
        ).strip()

        c1, c2, c3 = st.columns(3)

        with c1:
            only_abstracts = st.checkbox(
                "Only papers with abstracts",
                value=False,
                key=f"{key_prefix}_abstracts",
            )

        with c2:
            only_saved = False

            if include_saved_filter:
                only_saved = st.checkbox(
                    "Only saved by someone",
                    value=False,
                    key=f"{key_prefix}_saved",
                )

        with c3:
            if "journal" in out.columns:
                journals = sorted(
                    [
                        str(j)
                        for j in out["journal"].fillna("").unique().tolist()
                        if str(j).strip()
                    ]
                )
            else:
                journals = []

            selected_journals = st.multiselect(
                "Journal",
                journals,
                key=f"{key_prefix}_journals",
            )

    if search:
        search_cols = [
            c
            for c in ["title", "abstract", "authors", "journal", "configured_journal"]
            + list(NOTE_COLUMNS.values())
            if c in out.columns
        ]

        if search_cols:
            haystack = out[search_cols].fillna("").agg(" ".join, axis=1).str.lower()
            out = out[haystack.str.contains(re.escape(search.lower()), na=False)].copy()

    if only_abstracts and "abstract" in out.columns:
        out = out[out["abstract"].fillna("").str.strip() != ""].copy()

    if selected_journals and "journal" in out.columns:
        out = out[out["journal"].isin(selected_journals)].copy()

    if include_saved_filter and only_saved:
        out = add_saved_count(out)
        out = out[out["saved_count"] > 0].copy()

    return out


def render_save_box(row: pd.Series, key_prefix: str) -> None:
    with st.expander("Save to personal list / add note", expanded=False):
        person = st.selectbox(
            "Person",
            list(PEOPLE.keys()),
            key=f"{key_prefix}_person_{row['unique_key']}",
        )

        keep_col = KEEP_COLUMNS[person]
        note_col = NOTE_COLUMNS[person]

        current_keep = bool(int(row.get(keep_col, 0) or 0))
        current_note = text_value(row.get(note_col, ""))

        with st.form(key=f"{key_prefix}_form_{person}_{row['unique_key']}"):
            keep = st.checkbox("Keep this paper", value=current_keep)
            note = st.text_area("Personal note", value=current_note, height=90)
            submitted = st.form_submit_button("Save")

            if submitted:
                update_personal_choice(row["unique_key"], person, keep, note)
                st.success(f"Saved for {person}.")
                st.rerun()


def render_paper_card(
    row: pd.Series,
    key_prefix: str,
    show_save_box: bool = True,
    show_all_notes: bool = True,
) -> None:
    title = text_value(row.get("title", "")).strip() or "Untitled paper"
    journal = text_value(row.get("journal", "")).strip()
    configured_journal = text_value(row.get("configured_journal", "")).strip()
    published_date = text_value(row.get("published_date", "")).strip()
    authors = short_text(row.get("authors", ""), 220)
    abstract = short_text(row.get("abstract", ""), 1200)
    link = paper_link(row)

    st.markdown("---")
    st.markdown(f"### {title}")

    meta = " · ".join(
        [x for x in [journal or configured_journal, published_date[:10]] if x]
    )

    if meta:
        st.caption(meta)

    if authors:
        st.caption(f"Authors: {authors}")

    people = saved_by(row)

    if people:
        st.write("Saved by: " + ", ".join(people))

    if abstract:
        st.write(abstract)
    else:
        st.warning("No abstract available.")

    if link:
        st.link_button("Open paper", link)

    if show_all_notes:
        notes = note_items(row)

        if notes:
            with st.expander("Team notes", expanded=False):
                for name, note in notes:
                    st.markdown(f"**{name}:** {note}")

    if show_save_box:
        render_save_box(row, key_prefix=key_prefix)


def render_dataframe_summary(df: pd.DataFrame) -> None:
    cols = [
        c
        for c in ["title", "journal", "published_date", "authors"]
        if c in df.columns
    ]

    if not cols:
        return

    shown = df[cols].copy()

    for col in shown.columns:
        shown[col] = shown[col].fillna("").astype(str)

    st.dataframe(shown, use_container_width=True, hide_index=True)


def render_paper_list(
    df: pd.DataFrame,
    key_prefix: str,
    max_cards: int = 50,
    show_save_box: bool = True,
    show_all_notes: bool = True,
) -> None:
    if df.empty:
        st.info("No papers found.")
        return

    st.caption(f"{len(df):,} papers found.")

    mode = st.radio(
        "Display",
        ["Readable cards", "Compact table"],
        horizontal=True,
        key=f"{key_prefix}_display",
    )

    if mode == "Compact table":
        render_dataframe_summary(df)
        return

    upper = min(max_cards, max(5, len(df)))
    default = min(20, len(df), max_cards)

    n = st.slider(
        "Number of papers to show",
        min_value=5,
        max_value=upper,
        value=max(5, default),
        step=5,
        key=f"{key_prefix}_n",
    )

    for _, row in df.head(n).iterrows():
        render_paper_card(
            row,
            key_prefix=key_prefix,
            show_save_box=show_save_box,
            show_all_notes=show_all_notes,
        )


def render_journal_family_page(
    title: str,
    groups: dict[str, list[str]],
    key_prefix: str,
) -> None:
    st.title(title)

    df = load_papers()

    frames = []

    for journals in groups.values():
        frames.append(filter_by_journals(df, journals))

    if frames:
        all_family = pd.concat(frames, ignore_index=True)
        all_family = all_family.drop_duplicates(subset=["unique_key"])
    else:
        all_family = df.iloc[0:0].copy()

    all_family = apply_common_filters(all_family, key_prefix=f"{key_prefix}_all")

    st.caption(f"{len(all_family):,} papers in this journal family after filters.")

    for group_name, journals in groups.items():
        group_df = filter_by_journals(all_family, journals)

        safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", group_name).lower()

        with st.expander(f"{group_name} ({len(group_df):,})", expanded=True):
            render_paper_list(
                group_df,
                key_prefix=f"{key_prefix}_{safe_name}",
                max_cards=40,
            )
