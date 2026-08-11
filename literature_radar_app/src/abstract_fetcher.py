from __future__ import annotations

from typing import Any


def fetch_abstract_from_article_page(url: str, timeout: int = 25) -> str:
    return ""


def fetch_abstract_for_paper(paper: dict[str, Any], timeout: int = 25) -> str:
    return ""


def enrich_missing_abstract(paper: dict[str, Any]) -> dict[str, Any]:
    return paper
