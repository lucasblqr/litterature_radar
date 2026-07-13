from __future__ import annotations

import csv
import re
import time
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


INPUT_FILE = Path("doi_links.csv")
OUTPUT_FILE = Path("doi_abstracts_found.csv")
DEBUG_DIR = Path("debug_abstract_pages")


ABSTRACT_SELECTORS = [
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

    "section.article-header__abstract",
    "section.article-section__abstract",
    "section#article-section-abstract",
    "section#article-section-summary",
    "div.article-header__abstract",
    "div.Summary",
    "[data-test='abstract']",
    "[data-testid='abstract']",
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


def clean_text(text: str) -> str:
    text = unescape(text or "")

    if "<" in text and ">" in text:
        text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_abstract(text: str) -> str:
    text = clean_text(text)
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
        " Research in context ",
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


def normalize_doi_or_url(value: str) -> str:
    value = clean_text(value)

    if value.startswith("http://") or value.startswith("https://"):
        return value

    value = value.replace("doi:", "").strip()

    if value.startswith("10."):
        return f"https://doi.org/{value}"

    return value


def url_variants(url: str) -> list[str]:
    base = url.split("#")[0].rstrip("/")
    variants = [base]

    host = urlparse(base).netloc.lower()

    if "gh.bmj.com" in host and "/content/" in base:
        if not base.endswith(".full"):
            variants.append(base + ".full")

    if "thelancet.com" in host and "/article/" in base:
        clean_base = base.replace("?rss=yes", "").rstrip("/")
        if not clean_base.endswith("/fulltext"):
            variants.append(clean_base + "/fulltext")
            variants.append(clean_base + "/fulltext?rss=yes")

    out = []
    for v in variants:
        if v not in out:
            out.append(v)

    return out


def extract_from_meta_or_selectors(soup: BeautifulSoup) -> str:
    for selector in ABSTRACT_SELECTORS:
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

    return ""


def extract_after_heading(soup: BeautifulSoup) -> str:
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "strong"]):
        heading_text = clean_text(heading.get_text(" ", strip=True)).lower()

        if heading_text not in {"abstract", "summary"}:
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


def extract_lancet_summary_pattern(soup: BeautifulSoup) -> str:
    text = clean_abstract(soup.get_text(" ", strip=True))

    pattern = re.compile(
        r"(summary\s+background\s+.+?methods\s+.+?findings\s+.+?interpretation\s+.+?)(funding|research in context|introduction|references)",
        flags=re.I | re.S,
    )

    match = pattern.search(text)

    if not match:
        return ""

    abstract = clean_abstract(match.group(1))

    if looks_like_abstract(abstract):
        return abstract

    return ""


def scrape_abstract(url: str, session: requests.Session) -> dict:
    start_url = normalize_doi_or_url(url)

    if not start_url.startswith(("http://", "https://")):
        return {
            "input": url,
            "final_url": "",
            "abstract": "",
            "status": "invalid url",
        }

    tried = []
    final_url = ""

    try:
        r = session.get(start_url, timeout=30, allow_redirects=True)
        r.raise_for_status()
        final_url = r.url
        html = r.text
    except Exception as exc:
        return {
            "input": url,
            "final_url": "",
            "abstract": "",
            "status": f"could not open DOI: {exc}",
        }

    candidates = url_variants(final_url)

    for candidate in candidates:
        tried.append(candidate)

        try:
            r = session.get(candidate, timeout=30, allow_redirects=True)
            r.raise_for_status()
            final_url = r.url
            html = r.text
        except Exception as exc:
            print(f"Could not open variant {candidate}: {exc}")
            continue

        soup = BeautifulSoup(html, "html.parser")

        abstract = (
            extract_from_meta_or_selectors(soup)
            or extract_after_heading(soup)
            or extract_lancet_summary_pattern(soup)
        )

        if abstract:
            return {
                "input": url,
                "final_url": final_url,
                "abstract": abstract,
                "status": "found",
            }

        save_debug_html(url, html)

        time.sleep(1)

    return {
        "input": url,
        "final_url": final_url,
        "abstract": "",
        "status": "not found; tried: " + " | ".join(tried),
    }


def save_debug_html(input_url: str, html: str) -> None:
    DEBUG_DIR.mkdir(exist_ok=True)

    safe_name = re.sub(r"[^A-Za-z0-9]+", "_", input_url)[:80]
    path = DEBUG_DIR / f"{safe_name}.html"

    if not path.exists():
        path.write_text(html[:500000], encoding="utf-8", errors="ignore")


def read_input_rows() -> list[str]:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Could not find {INPUT_FILE}")

    rows = []

    with INPUT_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if "doi_or_url" not in reader.fieldnames:
            raise ValueError("CSV must have a column called doi_or_url")

        for row in reader:
            value = clean_text(row.get("doi_or_url", ""))
            if value:
                rows.append(value)

    return rows


def main() -> None:
    inputs = read_input_rows()
    session = make_session()

    results = []

    print(f"Checking {len(inputs)} DOI links")

    for i, value in enumerate(inputs, start=1):
        print(f"\n{i}/{len(inputs)}")
        print(value)

        result = scrape_abstract(value, session)
        results.append(result)

        if result["abstract"]:
            print(f"FOUND: {len(result['abstract'])} characters")
        else:
            print("NOT FOUND")
            print(result["status"])

        time.sleep(1)

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["input", "final_url", "status", "abstract"],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved results to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
