from __future__ import annotations

import argparse
import re
import sqlite3
import sys
import time
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import DB_PATH
from src.utils import clean_text


BMJ_SELECTORS = [
    "meta[name='citation_abstract']",
    "meta[name='dc.description']",
    "meta[name='description']",
    "meta[property='og:description']",
    "section#abstract",
    "section.abstract",
    "div.abstract",
    "div#abstract",
    "div.section.abstract",
    "div.article-section.abstract",
    "div.fulltext-view div.abstract",
    "div.article.abstract",
    "div#abstract-1",
]


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    return s


def clean_abstract(text: str) -> str:
    text = unescape(text or "")

    if "<" in text and ">" in text:
        text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)

    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^(abstract|summary)\s*[:.]?\s*", "", text, flags=re.I)

    stop_markers = [
        " Data availability statement ",
        " Ethics statements ",
        " Ethics approval ",
        " Acknowledgments ",
        " Footnotes ",
        " Contributors ",
        " Funding ",
        " Competing interests ",
        " Patient consent ",
        " Provenance and peer review ",
        " References ",
        " Request permissions ",
        " Article info ",
        " Introduction ",
    ]

    padded = f" {text} "
    for marker in stop_markers:
        idx = padded.lower().find(marker.lower())
        if idx > 250:
            text = padded[:idx].strip()
            break

    return clean_text(text)


def looks_like_abstract(text: str) -> bool:
    text = clean_abstract(text)

    if len(text) < 120:
        return False

    bad = [
        "cookies",
        "enable javascript",
        "sign in",
        "subscribe",
        "accept all cookies",
        "purchase access",
        "access this article",
    ]

    lower = text.lower()
    return not any(x in lower for x in bad)


def get_bmj_article_id(row: dict) -> str:
    text = " ".join(
        [
            clean_text(row.get("doi", "")),
            clean_text(row.get("url", "")),
        ]
    )

    match = re.search(r"bmjgh-\d{4}-(\d+)", text, flags=re.I)

    if not match:
        return ""

    return "e" + match.group(1)


def get_year_month(published_date: str) -> tuple[int | None, int | None]:
    published_date = clean_text(published_date)

    match = re.match(r"(\d{4})-(\d{1,2})", published_date)

    if not match:
        return None, None

    year = int(match.group(1))
    month = int(match.group(2))

    if month < 1 or month > 12:
        month = None

    return year, month


def bmj_volume_from_year(year: int) -> int:
    return year - 2015


def bmj_url_variants(row: dict) -> list[str]:
    url = clean_text(row.get("url", ""))
    doi = clean_text(row.get("doi", ""))
    published_date = clean_text(row.get("published_date", ""))

    variants = []

    article_id = get_bmj_article_id(row)
    year, month = get_year_month(published_date)

    if article_id and year:
        volume = bmj_volume_from_year(year)

        issue_candidates = []

        if month:
            issue_candidates.append(month)

        for issue in range(1, 13):
            if issue not in issue_candidates:
                issue_candidates.append(issue)

        for issue in issue_candidates:
            base = f"https://gh.bmj.com/content/{volume}/{issue}/{article_id}"
            variants.append(base)
            variants.append(base + ".full")

    for candidate in [url, doi]:
        candidate = clean_text(candidate)

        if not candidate:
            continue

        if candidate.startswith("10."):
            candidate = "https://doi.org/" + candidate

        if candidate.startswith(("http://", "https://")):
            host = urlparse(candidate).netloc.lower()

            if "gh.bmj.com" in host and "/content/" in candidate:
                base = candidate.split("#")[0].rstrip("/")
                variants.append(base)

                if not base.endswith(".full"):
                    variants.append(base + ".full")

    out = []
    for item in variants:
        if item and item not in out:
            out.append(item)

    return out


def extract_bmj_abstract(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for selector in BMJ_SELECTORS:
        tag = soup.select_one(selector)

        if not tag:
            continue

        if tag.name == "meta":
            text = tag.get("content", "")
        else:
            for bad in tag.select("script, style, nav, aside, figure, table, sup"):
                bad.decompose()

            text = tag.get_text(" ", strip=True)

        abstract = clean_abstract(text)

        if looks_like_abstract(abstract):
            return abstract

    for heading in soup.find_all(["h1", "h2", "h3", "h4", "strong"]):
        heading_text = clean_text(heading.get_text(" ", strip=True)).lower()

        if heading_text != "abstract":
            continue

        parts = []

        for sibling in heading.find_next_siblings():
            if sibling.name in ["h1", "h2", "h3"]:
                break

            text = sibling.get_text(" ", strip=True)
            if text:
                parts.append(text)

            if len(" ".join(parts)) > 6000:
                break

        abstract = clean_abstract(" ".join(parts))

        if looks_like_abstract(abstract):
            return abstract

    return ""


def scrape_bmj_abstract(row: dict, session: requests.Session) -> str:
    candidates = bmj_url_variants(row)

    if not candidates:
        print("  No BMJ URL candidates")
        return ""

    for candidate in candidates:
        try:
            r = session.get(candidate, timeout=30, allow_redirects=True)
            r.raise_for_status()
        except Exception as exc:
            print(f"  Could not open {candidate}: {exc}")
            continue

        abstract = extract_bmj_abstract(r.text)

        if abstract:
            print(f"  Found from {candidate}")
            return abstract

        time.sleep(1)

    return ""


def get_missing_bmj_rows(limit: int) -> list[dict]:
    query = """
    SELECT unique_key, title, journal, configured_journal, doi, url, published_date, abstract
    FROM papers
    WHERE
        (
            lower(COALESCE(journal, '')) LIKE '%bmj global health%'
            OR lower(COALESCE(journal, '')) LIKE '%bmj glob health%'
            OR lower(COALESCE(configured_journal, '')) LIKE '%bmj global health%'
            OR lower(COALESCE(configured_journal, '')) LIKE '%bmj glob health%'
            OR lower(COALESCE(url, '')) LIKE '%gh.bmj.com%'
            OR lower(COALESCE(url, '')) LIKE '%bmjgh-%'
            OR lower(COALESCE(doi, '')) LIKE '%bmjgh-%'
        )
        AND COALESCE(TRIM(abstract), '') = ''
    ORDER BY published_date DESC
    LIMIT ?
    """

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(query, (limit,)).fetchall()]


def update_abstract(unique_key: str, abstract: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            UPDATE papers
            SET abstract = ?,
                source = CASE
                    WHEN COALESCE(source, '') LIKE '%bmj_abstract_scrape%'
                    THEN source
                    WHEN COALESCE(source, '') = ''
                    THEN 'bmj_abstract_scrape'
                    ELSE COALESCE(source, '') || '+bmj_abstract_scrape'
                END
            WHERE unique_key = ?
            """,
            (abstract, unique_key),
        )
        conn.commit()


def backfill(limit: int = 50, dry_run: bool = False) -> None:
    rows = get_missing_bmj_rows(limit)

    print(f"Missing BMJ Global Health abstracts to check: {len(rows)}")

    session = make_session()
    found = 0

    for i, row in enumerate(rows, start=1):
        title = clean_text(row.get("title", ""))
        doi = clean_text(row.get("doi", ""))
        url = clean_text(row.get("url", ""))
        published_date = clean_text(row.get("published_date", ""))

        print(f"\n{i}/{len(rows)}")
        print(title[:160])
        print(f"DOI: {doi}")
        print(f"URL: {url}")
        print(f"Published date: {published_date}")

        abstract = scrape_bmj_abstract(row, session)

        if abstract:
            found += 1
            print(f"  Abstract found: {len(abstract)} characters")

            if not dry_run:
                update_abstract(row["unique_key"], abstract)
        else:
            print("  Still missing")

        time.sleep(1)

    print(f"\nDone. Found {found}/{len(rows)} BMJ abstracts.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    backfill(limit=args.limit, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
