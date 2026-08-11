from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st
from supabase import Client, create_client


TABLE_NAME = "paper_reviews"


def supabase_configured() -> bool:
    """Return True when the Streamlit Supabase secrets are available."""
    try:
        config = st.secrets["supabase"]
        url = str(config["url"]).strip()
        key = str(config["key"]).strip()
        return bool(url and key)
    except Exception:
        return False


@st.cache_resource
def get_supabase_client() -> Client:
    """Create one reusable Supabase client."""
    config = st.secrets["supabase"]

    return create_client(
        str(config["url"]),
        str(config["key"]),
    )


def fetch_all_reviews(page_size: int = 1000) -> list[dict[str, Any]]:
    """Download all shared Yes/No choices and notes."""
    if not supabase_configured():
        return []

    client = get_supabase_client()

    rows: list[dict[str, Any]] = []
    start = 0

    while True:
        response = (
            client.table(TABLE_NAME)
            .select("id,paper_id,reviewer,keep,note,updated_at")
            .order("id")
            .range(start, start + page_size - 1)
            .execute()
        )

        batch = response.data or []
        rows.extend(batch)

        if len(batch) < page_size:
            break

        start += page_size

    return rows


def save_review(
    paper_id: str,
    reviewer: str,
    keep: bool,
    note: str,
) -> None:
    """Insert or update one person's review of one paper."""
    if not supabase_configured():
        raise RuntimeError("Supabase is not configured.")

    payload = {
        "paper_id": paper_id,
        "reviewer": reviewer,
        "keep": bool(keep),
        "note": note or "",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    (
        get_supabase_client()
        .table(TABLE_NAME)
        .upsert(
            payload,
            on_conflict="paper_id,reviewer",
        )
        .execute()
    )
