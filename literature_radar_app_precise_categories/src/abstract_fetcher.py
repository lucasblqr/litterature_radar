from __future__ import annotations

import json
import re
import time
import xml.etree.ElementTree as ET
from html import unescape
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .utils import clean_text


PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


TARGET_JOURNAL_TERMS = [
    "BMJ Global Health",
    "BMJ Glob Health",
    "The Lancet Global Health",
    "Lancet Global Health",
    "Lancet Glob Health",
    "The Lancet. Global health",
]


META_NAMES = [
    "citation_abstract",
    "dc.description",
    "DC.Description",
    "description",
    "og:description",
    "twitter:description",
]

ABSTRACT_SELECTORS = [
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


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 LiteratureRadar/0.1 "
                "(academic metadata collection; mailto:replace-with-your-email@example.com)"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    return s


def _clean_abstract(text: str) -> str:
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
        " Research in context ",
    ]

    padded = f" {text} "
    for marker in stop_markers:
        idx = padded.lower().find(marker.lower())
        if idx > 250:
            text = padded[:idx].strip()
            break

    return clean_text(text)


def _looks_like_abstract(text: str) -> bool:
    text = _clean_abstract(text)

    if len(text) < 100:
        return False

    bad_bits = [
        "cookies",
        "enable javascript",
        "sign in",
        "subscribe",
        "we use cookies",
        "accept all cookies",
        "access this article",
        "purchase access",
    ]

    lower = text.lower()
    return not any(bad in lower for bad in bad_bits)


def _is_target_journal(paper: dict[str, Any]) -> bool:
    text = " ".join(
        [
            str(paper.get("journal", "")),
            str(paper.get("configured_journal", "")),
            str(paper.get("url", "")),
        ]
    ).lower()

    return (
        "bmj global health" in text
        or "bmj glob health" in text
        or "gh.bmj.com" in text
        or "lancet global health" in text
        or "lancet glob health" in text
        or "/journals/langlo/" in text
    )


def _abstract_from_pubmed_xml(root: ET.Element) -> dict[str, str]:
    abstracts = {}

    for article in root.findall(".//PubmedArticle"):
        pmid_el = article.find(".//MedlineCitation/PMID")
        if pmid_el is None or not pmid_el.text:
            continue

        pmid = pmid_el.text.strip()
        parts = []

        for node in article.findall(".//Abstract/AbstractText"):
            label = clean_text(node.attrib.get("Label", ""))
            text = clean_text(" ".join(node.itertext()))

            if not text:
                continue

            if label:
                parts.append(f"{label}: {text}")
            else:
                parts.append(text)

        abstract = _clean_abstract(" ".join(parts))

        if _looks_like_abstract(abstract):
            abstracts[pmid] = abstract

    return abstracts


def _fetch_pubmed_abstract_for_ids(ids: list[str], session: requests.Session) -> str:
    if not ids:
        return ""

    try:
        r = session.get(
            PUBMED_EFETCH_URL,
            params={
                "db": "pubmed",
                "id": ",".join(ids),
                "retmode": "xml",
            },
            timeout=30,
        )
        r.raise_for_status()
        root = ET.fromstring(r.content)
    except Exception as exc:
        print(f"[PubMed abstract fallback] efetch failed: {exc}")
        return ""

    abstracts = _abstract_from_pubmed_xml(root)

    for pmid in ids:
        abstract = abstracts.get(str(pmid))
        if abstract:
            print(f"[PubMed abstract fallback] Found abstract for PMID {pmid}")
            return abstract

    return ""


def _search_pubmed_ids(query: str, session: requests.Session, retmax: int = 5) -> list[str]:
    if not query:
        return []

    try:
        r = session.get(
            PUBMED_ESEARCH_URL,
            params={
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": retmax,
                "sort": "relevance",
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("esearchresult", {}).get("idlist", [])
    except Exception as exc:
        print(f"[PubMed abstract fallback] esearch failed: {exc}")
        return []


def _pubmed_abstract_by_doi(paper: dict[str, Any], session: requests.Session) -> str:
    doi = clean_text(paper.get("doi", ""))

    if not doi:
        url = clean_text(paper.get("url", ""))
        match = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", url, flags=re.I)
        doi = clean_text(match.group(0)) if match else ""

    if not doi:
        return ""

    ids = _search_pubmed_ids(f'"{doi}"[AID]', session, retmax=5)
    abstract = _fetch_pubmed_abstract_for_ids(ids, session)

    if abstract:
        print("[PubMed abstract fallback] Found abstract by DOI")

    return abstract


def _pubmed_abstract_by_title(paper: dict[str, Any], session: requests.Session) -> str:
    title = clean_text(paper.get("title", ""))

    if len(title) < 20:
        return ""

    journal_query = " OR ".join(
        [
            f'"{j}"[Journal]'
            for j in TARGET_JOURNAL_TERMS
        ]
        + [
            f'"{j}"[TA]'
            for j in TARGET_JOURNAL_TERMS
        ]
    )

    query = f'"{title}"[Title] AND ({journal_query})'
    ids = _search_pubmed_ids(query, session, retmax=5)
    abstract = _fetch_pubmed_abstract_for_ids(ids, session)

    if abstract:
        print("[PubMed abstract fallback] Found abstract by title")

    return abstract


def _abstract_from_meta(soup: BeautifulSoup) -> str:
    for name in META_NAMES:
        tag = soup.find("meta", attrs={"name": name})
        if not tag:
            tag = soup.find("meta", attrs={"property": name})

        if tag and tag.get("content"):
            abstract = _clean_abstract(tag.get("content", ""))
            if _looks_like_abstract(abstract):
                return abstract

    return ""


def _walk_json(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from _walk_json(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_json(item)


def _abstract_from_jsonld(soup: BeautifulSoup) -> str:
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = script.string or script.get_text(" ", strip=True)

        if not raw:
            continue

        try:
            data = json.loads(raw)
        except Exception:
            continue

        for item in _walk_json(data):
            abstract = item.get("abstract") or item.get("description")

            if isinstance(abstract, list):
                abstract = " ".join(str(x) for x in abstract)

            if abstract:
                abstract = _clean_abstract(str(abstract))
                if _looks_like_abstract(abstract):
                    return abstract

    return ""


def _abstract_from_selectors(soup: BeautifulSoup) -> str:
    for selector in ABSTRACT_SELECTORS:
        tag = soup.select_one(selector)

        if not tag:
            continue

        for bad in tag.select("script, style, nav, aside, figure, table, sup"):
            bad.decompose()

        abstract = _clean_abstract(tag.get_text(" ", strip=True))

        if _looks_like_abstract(abstract):
            return abstract

    return ""


def _abstract_after_heading(soup: BeautifulSoup) -> str:
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

            if len(" ".join(parts)) > 5000:
                break

        abstract = _clean_abstract(" ".join(parts))

        if _looks_like_abstract(abstract):
            return abstract

    return ""


def _url_variants(url: str) -> list[str]:
    url = clean_text(url)
    if not url:
        return []

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
    for item in variants:
        if item not in out:
            out.append(item)

    return out


def _web_abstract_from_article_page(url: str, session: requests.Session) -> str:
    for candidate in _url_variants(url):
        try:
            r = session.get(candidate, timeout=30, allow_redirects=True)
            r.raise_for_status()
        except Exception as exc:
            print(f"[Web abstract fallback] Could not open {candidate}: {exc}")
            continue

        content_type = r.headers.get("content-type", "").lower()
        if "html" not in content_type and "xml" not in content_type:
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        abstract = (
            _abstract_from_meta(soup)
            or _abstract_from_jsonld(soup)
            or _abstract_from_selectors(soup)
            or _abstract_after_heading(soup)
        )

        time.sleep(0.8)

        if abstract:
            print(f"[Web abstract fallback] Found abstract from {urlparse(r.url).netloc}")
            return abstract

    return ""


def fetch_abstract_for_paper(paper: dict[str, Any]) -> str:
    session = _session()

    if _is_target_journal(paper):
        abstract = (
            _pubmed_abstract_by_doi(paper, session)
            or _pubmed_abstract_by_title(paper, session)
        )

        if abstract:
            return abstract

    url = clean_text(paper.get("url", ""))

    if url.startswith(("http://", "https://")):
        return _web_abstract_from_article_page(url, session)

    return ""


def fetch_abstract_from_article_page(url: str, timeout: int = 30) -> str:
    paper = {
        "url": url,
        "title": "",
        "journal": "",
        "configured_journal": "",
        "doi": "",
    }

    return fetch_abstract_for_paper(paper)


def enrich_missing_abstract(paper: dict[str, Any]) -> dict[str, Any]:
    current = clean_text(paper.get("abstract", ""))

    if current:
        return paper

    abstract = fetch_abstract_for_paper(paper)

    if not abstract:
        print(
            "[Abstract fallback] Still missing: "
            + clean_text(paper.get("journal", ""))
            + " | "
            + clean_text(paper.get("title", ""))[:120]
        )
        return paper

    updated = dict(paper)
    updated["abstract"] = abstract

    source = clean_text(updated.get("source", ""))
    if "abstract_fallback" not in source:
        updated["source"] = f"{source}+abstract_fallback" if source else "abstract_fallback"

    return updated
