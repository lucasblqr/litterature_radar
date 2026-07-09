from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .config import DB_PATH


SCHEMA = '''
CREATE TABLE IF NOT EXISTS papers (
    unique_key TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    journal TEXT,
    configured_journal TEXT,
    journal_group TEXT,
    source TEXT,
    doi TEXT,
    url TEXT,
    published_date TEXT,
    authors TEXT,
    abstract TEXT,
    fetched_at TEXT,
    score_strong INTEGER DEFAULT 0,
    score_econ INTEGER DEFAULT 0,
    score_health INTEGER DEFAULT 0,
    score_random INTEGER DEFAULT 0,
    score_preventive INTEGER DEFAULT 0,
    score_hypertension INTEGER DEFAULT 0,
    score_mental_models INTEGER DEFAULT 0,
    reasons_strong TEXT DEFAULT '[]',
    reasons_econ TEXT DEFAULT '[]',
    reasons_health TEXT DEFAULT '[]',
    reasons_random TEXT DEFAULT '[]',
    reasons_preventive TEXT DEFAULT '[]',
    reasons_hypertension TEXT DEFAULT '[]',
    reasons_mental_models TEXT DEFAULT '[]',
    review_status TEXT DEFAULT 'new',
    notes TEXT DEFAULT '',
    feedback_nikkil INTEGER DEFAULT 0,
    feedback_anna INTEGER DEFAULT 0,
    feedback_caterina INTEGER DEFAULT 0,
    feedback_michaela INTEGER DEFAULT 0,
    feedback_vasanthi INTEGER DEFAULT 0
);
'''

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_papers_published_date ON papers(published_date);",
    "CREATE INDEX IF NOT EXISTS idx_papers_score_strong ON papers(score_strong);",
    "CREATE INDEX IF NOT EXISTS idx_papers_score_econ ON papers(score_econ);",
    "CREATE INDEX IF NOT EXISTS idx_papers_score_health ON papers(score_health);",
    "CREATE INDEX IF NOT EXISTS idx_papers_score_random ON papers(score_random);",
    "CREATE INDEX IF NOT EXISTS idx_papers_score_preventive ON papers(score_preventive);",
    "CREATE INDEX IF NOT EXISTS idx_papers_score_hypertension ON papers(score_hypertension);",
    "CREATE INDEX IF NOT EXISTS idx_papers_score_mental_models ON papers(score_mental_models);",
    "CREATE INDEX IF NOT EXISTS idx_papers_journal ON papers(journal);",
]


def connect(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


FEEDBACK_COLUMNS = {
    "score_preventive": "INTEGER DEFAULT 0",
    "score_hypertension": "INTEGER DEFAULT 0",
    "score_mental_models": "INTEGER DEFAULT 0",
    "reasons_preventive": "TEXT DEFAULT '[]'",
    "reasons_hypertension": "TEXT DEFAULT '[]'",
    "reasons_mental_models": "TEXT DEFAULT '[]'",
    "feedback_nikkil": "INTEGER DEFAULT 0",
    "feedback_anna": "INTEGER DEFAULT 0",
    "feedback_caterina": "INTEGER DEFAULT 0",
    "feedback_michaela": "INTEGER DEFAULT 0",
    "feedback_vasanthi": "INTEGER DEFAULT 0",
}


def init_db(db_path: str | Path = DB_PATH) -> None:
    with connect(db_path) as conn:
        conn.execute(SCHEMA)

        existing_cols = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(papers)").fetchall()
        }
        for col, definition in FEEDBACK_COLUMNS.items():
            if col not in existing_cols:
                conn.execute(f"ALTER TABLE papers ADD COLUMN {col} {definition}")

        for idx in INDEXES:
            conn.execute(idx)
        conn.commit()


def upsert_papers(papers: Iterable[dict], db_path: str | Path = DB_PATH) -> int:
    init_db(db_path)
    count = 0
    sql = '''
    INSERT INTO papers (
        unique_key, title, journal, configured_journal, journal_group, source,
        doi, url, published_date, authors, abstract, fetched_at,
        score_strong, score_econ, score_health, score_random,
        score_preventive, score_hypertension, score_mental_models,
        reasons_strong, reasons_econ, reasons_health, reasons_random,
        reasons_preventive, reasons_hypertension, reasons_mental_models
    )
    VALUES (
        :unique_key, :title, :journal, :configured_journal, :journal_group, :source,
        :doi, :url, :published_date, :authors, :abstract, :fetched_at,
        :score_strong, :score_econ, :score_health, :score_random,
        :score_preventive, :score_hypertension, :score_mental_models,
        :reasons_strong, :reasons_econ, :reasons_health, :reasons_random,
        :reasons_preventive, :reasons_hypertension, :reasons_mental_models
    )
    ON CONFLICT(unique_key) DO UPDATE SET
        title = excluded.title,
        journal = excluded.journal,
        configured_journal = excluded.configured_journal,
        journal_group = excluded.journal_group,
        source = excluded.source,
        doi = excluded.doi,
        url = excluded.url,
        published_date = excluded.published_date,
        authors = excluded.authors,
        abstract = excluded.abstract,
        fetched_at = excluded.fetched_at,
        score_strong = excluded.score_strong,
        score_econ = excluded.score_econ,
        score_health = excluded.score_health,
        score_random = excluded.score_random,
        score_preventive = excluded.score_preventive,
        score_hypertension = excluded.score_hypertension,
        score_mental_models = excluded.score_mental_models,
        reasons_strong = excluded.reasons_strong,
        reasons_econ = excluded.reasons_econ,
        reasons_health = excluded.reasons_health,
        reasons_random = excluded.reasons_random,
        reasons_preventive = excluded.reasons_preventive,
        reasons_hypertension = excluded.reasons_hypertension,
        reasons_mental_models = excluded.reasons_mental_models;
    '''
    with connect(db_path) as conn:
        for paper in papers:
            row = dict(paper)
            for key in [
                "reasons_strong", "reasons_econ", "reasons_health", "reasons_random",
                "reasons_preventive", "reasons_hypertension", "reasons_mental_models",
            ]:
                if not isinstance(row.get(key), str):
                    row[key] = json.dumps(row.get(key, []), ensure_ascii=False)
            for key in [
                "score_strong", "score_econ", "score_health", "score_random",
                "score_preventive", "score_hypertension", "score_mental_models",
            ]:
                row[key] = int(row.get(key, 0) or 0)
            conn.execute(sql, row)
            count += 1
        conn.commit()
    return count


def count_papers(db_path: str | Path = DB_PATH) -> int:
    init_db(db_path)
    with connect(db_path) as conn:
        return conn.execute("SELECT COUNT(*) AS n FROM papers").fetchone()["n"]


def get_latest_update(db_path: str | Path = DB_PATH) -> str | None:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute("SELECT MAX(fetched_at) AS fetched_at FROM papers").fetchone()
        return row["fetched_at"] if row else None


def load_papers(
    score_col: str | None = None,
    min_score: int = 0,
    days: int | None = None,
    search: str = "",
    status: str = "All",
    limit: int = 500,
    db_path: str | Path = DB_PATH,
):
    import pandas as pd

    init_db(db_path)
    where = []
    params = {}

    if score_col:
        where.append(f"{score_col} >= :min_score")
        params["min_score"] = min_score

    if days:
        where.append("published_date >= date('now', :days_back)")
        params["days_back"] = f"-{int(days)} days"

    if search:
        where.append("(lower(title) LIKE :search OR lower(journal) LIKE :search OR lower(abstract) LIKE :search)")
        params["search"] = f"%{search.lower()}%"

    if status != "All":
        where.append("review_status = :status")
        params["status"] = status

    where_sql = "WHERE " + " AND ".join(where) if where else ""
    order_col = score_col or "published_date"
    direction = "DESC"

    query = f'''
    SELECT *
    FROM papers
    {where_sql}
    ORDER BY {order_col} {direction}, published_date DESC
    LIMIT :limit
    '''
    params["limit"] = limit

    with connect(db_path) as conn:
        return pd.read_sql_query(query, conn, params=params)


def update_review_status(unique_key: str, status: str, notes: str = "", db_path: str | Path = DB_PATH) -> None:
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            "UPDATE papers SET review_status = ?, notes = ? WHERE unique_key = ?",
            (status, notes, unique_key),
        )
        conn.commit()


def update_feedback_bulk(rows: list[dict], db_path: str | Path = DB_PATH) -> None:
    init_db(db_path)
    cols = [
        "feedback_nikkil",
        "feedback_anna",
        "feedback_caterina",
        "feedback_michaela",
        "feedback_vasanthi",
    ]
    with connect(db_path) as conn:
        for row in rows:
            values = [1 if row.get(col) else 0 for col in cols]
            values.append(row["unique_key"])
            conn.execute(
                '''
                UPDATE papers
                SET feedback_nikkil = ?,
                    feedback_anna = ?,
                    feedback_caterina = ?,
                    feedback_michaela = ?,
                    feedback_vasanthi = ?
                WHERE unique_key = ?
                ''',
                values,
            )
        conn.commit()
