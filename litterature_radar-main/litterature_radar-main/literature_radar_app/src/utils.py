from __future__ import annotations

import html
import re
from datetime import date, datetime
from typing import Any


_TAG_RE = re.compile(r"<[^>]+>")


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = " ".join(str(x) for x in value if x)
    value = html.unescape(str(value))
    value = _TAG_RE.sub(" ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize(value: Any) -> str:
    value = clean_text(value).lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    if value.startswith("the "):
        value = value[4:]
    return value


def safe_date_from_parts(parts: Any) -> str | None:
    try:
        if not parts:
            return None
        vals = parts[0] if isinstance(parts[0], list) else parts
        year = int(vals[0])
        month = int(vals[1]) if len(vals) > 1 else 1
        day = int(vals[2]) if len(vals) > 2 else 1
        return date(year, month, day).isoformat()
    except Exception:
        return None


def today_iso() -> str:
    return date.today().isoformat()


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    value = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y %b %d", "%Y %B %d", "%Y %b", "%Y %B", "%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    match = re.search(r"(\d{4})", value)
    if match:
        return date(int(match.group(1)), 1, 1)
    return None


def make_unique_key(doi: str | None, title: str, journal: str) -> str:
    doi_norm = normalize(doi)
    if doi_norm:
        return f"doi:{doi_norm}"
    return f"title:{normalize(journal)}:{normalize(title)}"


def journal_matches(candidate: str, journal: dict[str, Any]) -> bool:
    candidate_norm = normalize(candidate)
    targets = [journal.get("name", ""), journal.get("short_name", "")]
    targets.extend(journal.get("aliases", []) or [])
    target_norms = {normalize(t) for t in targets if t}
    return candidate_norm in target_norms
