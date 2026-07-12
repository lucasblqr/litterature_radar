from __future__ import annotations

import json
import re
import time
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from html import unescape
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .utils import clean_text


BMJ_RSS_FEEDS = [
    "https://gh.bmj.com/rss/recent.xml",
    "https://gh.bmj.com/rss/current.xml",
]

META_NAMES = [
    "citation_abstract",
    "dc.description",
    "description",
    "og:description",
    "twitter:description",
]

GENERIC_SELECTORS = [
    "section#abstract",
    "section.abstract",
    "div.abstract",
    "div#abstract",
    "div#Abs1-content",
    "div.abstractSection",
    "div.hlFld-Abstract",
    "section[data-title='Abstract']",
    "[data-test='abstract']",
    "[data-testid='abstract']",
]

BMJ_SELECTORS = [
    "div.section.abstract",
    "section.abstract",
    "div.abstract",
    "div#abstract-1",
    "div#abstract",
    "div.article.abstract",
    "div.article-section.abstract",
    "div.fulltext-view div.abstract",
]

LANCET_SELECTORS = [
    "section.article-header__abstract",
    "section.article-section__abstract",
    "section#article-section-abstract",
    "section#article-section-summary",
    "div.article-header__abstract",
    "div.abstract",
    "div.Summary",
    "section[data-test='abstract']",
    "section[data-testid='abstract']",
]


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36 LiteratureRadar/0.1"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
        }
    )
    return s


def _strip_html(text: str) -> str:
    text = unescape(text or "")
    if "<" in text and ">" in text:
        text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
    return text


def _clean_abstract(text: str) -> str:
    text = _strip_html(text)
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
    ]

    padded = f" {text} "
    for marker in stop_markers:
        idx = padded.lower().find(marker.lower())
        if idx > 200:
            text = padded[:idx].strip()
            break

    return clean_text(text)


def _looks_like_abstract(text: str) -> bool:
    text = _clean_abstract(text)
    if len(text) < 120:
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
    if any(b in lower for b in bad_bits):
        return False

    return True


def _domain(url: str) -> str:
    return urlparse(url or "").netloc.lower()


def _is_bmj(paper: dict[str, Any], url: str) -> bool:
    txt = " ".join(
        [
            str(paper.get("journal", "")),
            str(paper.get("configured_journal", "")),
            url,
        ]
    ).lower()
    return "bmj global health" in txt or "gh.bmj.com" in txt


def _is_lancet_global_health(paper: dict[str, Any], url: str) -> bool:
    txt = " ".join(
        [
            str(paper.get("journal", "")),
            str(paper.get("configured_journal", "")),
            url,
        ]
    ).lower()
    return "lancet global health" in txt or "/journals/langlo/" in txt


def _tag_text(tag) -> str:
    if not tag:
        return ""

    tag = BeautifulSoup(str(tag), "html.parser")

    for bad in tag.select("script, style, nav, aside, figure, table, sup"):
        bad.decompose()

    return _clean_abstract(tag.get_text(" ", strip=True))


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
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})

    for script in scripts:
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


def _abstract_from_selectors(soup: BeautifulSoup, selectors: list[str]) -> str:
    for selector in selectors:
        tag = soup.select_one(selector)
        if not tag:
            continue

        text = _tag_text(tag)
        if _looks_like_abstract(text):
            return text

    return ""


def _abstract_after_heading(soup: BeautifulSoup, headings: set[str]) -> str:
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "strong"]):
        heading_text = clean_text(heading.get_text(" ", strip=True)).lower()

        if heading_text not in headings:
            continue

        parts = []

        for sibling in heading.find_next_siblings():
            if sibling.name in ["h1", "h2"]:
                break

            text = _tag_text(sibling)
            if text:
                parts.append(text)

            if len(" ".join(parts)) > 5000:
                break

        text = _clean_abstract(" ".join(parts))
        if _looks_like_abstract(text):
            return text

        parent = heading.find_parent(["section", "div", "article"])
        parent_text = _tag_text(parent)
        if _looks_like_abstract(parent_text):
            return parent_text

    return ""


def _abstract_from_lancet_structure(soup: BeautifulSoup) -> str:
    useful_words = {"background", "methods", "findings", "interpretation"}

    candidates = soup.find_all(["section", "div", "article"])
    for tag in candidates:
        text = _tag_text(tag)
        lower = text.lower()

        hits = sum(1 for word in useful_words if re.search(rf"\b{word}\b", lower))
        if hits >= 3 and _looks_like_abstract(text):
            return text

    page_text = _clean_abstract(soup.get_text(" ", strip=True))
    pattern = re.compile(
        r"(summary\s+background\s+.+?interpretation\s+.+?)(funding|introduction|research in context|methods|references)",
        flags=re.I | re.S,
    )
    match = pattern.search(page_text)
    if match:
        text = _clean_abstract(match.group(1))
        if _looks_like_abstract(text):
            return text

    return ""


def _extract_bmj_abstract(soup: BeautifulSoup) -> str:
    return (
        _abstract_from_meta(soup)
        or _abstract_from_jsonld(soup)
        or _abstract_from_selectors(soup, BMJ_SELECTORS)
        or _abstract_after_heading(soup, {"abstract"})
        or _abstract_from_selectors(soup, GENERIC_SELECTORS)
    )


def _extract_lancet_abstract(soup: BeautifulSoup) -> str:
    return (
        _abstract_from_meta(soup)
        or _abstract_from_jsonld(soup)
        or _abstract_from_selectors(soup, LANCET_SELECTORS)
        or _abstract_after_heading(soup, {"summary", "abstract"})
        or _abstract_from_lancet_structure(soup)
        or _abstract_from_selectors(soup, GENERIC_SELECTORS)
    )


def _extract_generic_abstract(soup: BeautifulSoup) -> str:
    return (
        _abstract_from_meta(soup)
        or _abstract_from_jsonld(soup)
        or _abstract_from_selectors(soup, GENERIC_SELECTORS)
        or _abstract_after_heading(soup, {"summary", "abstract"})
    )


def _url_variants(url: str, final_url: str | None = None) -> list[str]:
    variants = []

    for candidate in [url, final_url or ""]:
        candidate = (candidate or "").strip()
        if not candidate:
            continue

        clean = candidate.split("#")[0].rstrip("/")
        if clean not in variants:
            variants.append(clean)

        host = _domain(clean)

        if "gh.bmj.com" in host and "/content/" in clean:
            if not clean.endswith(".full"):
                variants.append(clean + ".full")
            else:
                variants.append(clean.replace(".full", ""))

        if "thelancet.com" in host and "/article/" in clean:
            base = clean.replace("?rss=yes", "").rstrip("/")

            if not base.endswith("/fulltext"):
                variants.append(base + "/fulltext")
                variants.append(base + "/fulltext?rss=yes")
            else:
                variants.append(base + "?rss=yes")
                variants.append(base.replace("/fulltext", ""))

    out = []
    for item in variants:
        if item and item not in out:
            out.append(item)

    return out[:6]


def _fetch_html(url: str, session: requests.Session, timeout: int = 25) -> tuple[str, str]:
    try:
        response = session.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
    except Exception as exc:
        print(f"[Abstract web scrape] Could not open {url}: {exc}")
        return "", ""

    content_type = response.headers.get("content-type", "").lower()
    if "html" not in content_type and "xml" not in content_type:
        return "", response.url

    return response.text, response.url


def _similar(a: str, b: str) -> float:
    a = clean_text(a).lower()
    b = clean_text(b).lower()

    if not a or not b:
        return 0.0

    return SequenceMatcher(None, a, b).ratio()


def _bmj_abstract_from_rss(paper: dict[str, Any], session: requests.Session) -> str:
    title = clean_text(paper.get("title", ""))
    url = clean_text(paper.get("url", ""))

    if not title and not url:
        return ""

    for feed_url in BMJ_RSS_FEEDS:
        try:
            r = session.get(feed_url, timeout=25)
            r.raise_for_status()
            root = ET.fromstring(r.content)
        except Exception as exc:
            print(f"[BMJ RSS abstract] Could not read {feed_url}: {exc}")
            continue

        for item in root.findall(".//item"):
            item_title = clean_text(item.findtext("title", ""))
            item_link = clean_text(item.findtext("link", ""))

            match_by_url = bool(url and item_link and item_link.rstrip("/") in url.rstrip("/"))
            match_by_title = _similar(title, item_title) > 0.88

            if not match_by_url and not match_by_title:
                continue

            parts = []

            description = item.findtext("description", "")
            if description:
                parts.append(description)

            for child in item:
                if child.tag.lower().endswith("encoded") and child.text:
                    parts.append(child.text)

            abstract = _clean_abstract(" ".join(parts))
            if _looks_like_abstract(abstract):
                print("[BMJ RSS abstract] Found abstract")
                return abstract

    return ""


def fetch_abstract_for_paper(paper: dict[str, Any], timeout: int = 25) -> str:
    url = clean_text(paper.get("url", ""))
    if not url.startswith(("http://", "https://")):
        return ""

    session = _session()
    seen = set()
    queue = _url_variants(url)

    while queue:
        current_url = queue.pop(0)

        if current_url in seen:
            continue

        seen.add(current_url)

        html, final_url = _fetch_html(current_url, session, timeout=timeout)
        time.sleep(0.8)

        if final_url:
            for variant in _url_variants(current_url, final_url):
                if variant not in seen and variant not in queue:
                    queue.append(variant)

        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        check_url = final_url or current_url

        if _is_bmj(paper, check_url):
            abstract = _extract_bmj_abstract(soup)
        elif _is_lancet_global_health(paper, check_url):
            abstract = _extract_lancet_abstract(soup)
        else:
            abstract = _extract_generic_abstract(soup)

        if abstract:
            print(f"[Abstract web scrape] Found abstract from {_domain(check_url)}")
            return abstract

    if _is_bmj(paper, url):
        abstract = _bmj_abstract_from_rss(paper, session)
        if abstract:
            return abstract

    return ""


def fetch_abstract_from_article_page(url: str, timeout: int = 25) -> str:
    paper = {"url": url, "title": "", "journal": "", "configured_journal": ""}
    return fetch_abstract_for_paper(paper, timeout=timeout)


def enrich_missing_abstract(paper: dict[str, Any]) -> dict[str, Any]:
    if clean_text(paper.get("abstract", "")):
        return paper

    abstract = fetch_abstract_for_paper(paper)

    if not abstract:
        return paper

    updated = dict(paper)
    updated["abstract"] = abstract

    source = clean_text(updated.get("source", ""))
    if "web_abstract" not in source:
        updated["source"] = f"{source}+web_abstract" if source else "web_abstract"

    return updated
