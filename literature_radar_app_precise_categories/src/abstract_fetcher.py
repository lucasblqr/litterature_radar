from __future__ import annotations

import json
import re
import time
from html import unescape
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .utils import clean_text


ABSTRACT_META_NAMES = [
    "citation_abstract",
    "dc.description",
    "description",
    "og:description",
    "twitter:description",
]

ABSTRACT_SELECTORS = [
    "section#abstract",
    "section.abstract",
    "div.abstract",
    "div.article__abstract",
    "div.c-article-section__content",
    "div#Abs1-content",
    "div.abstractSection",
    "div.hlFld-Abstract",
    "section[data-title='Abstract']",
]


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": "LiteratureRadar/0.1 (academic metadata collection; contact: replace-with-your-email@example.com)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
    )
    return s


def _looks_like_abstract(text: str) -> bool:
    text = clean_text(text)
    if len(text) < 80:
        return False
    bad = ["cookies", "enable javascript", "subscribe", "sign in", "accept all"]
    return not any(b in text.lower() for b in bad)


def _clean_abstract(text: str) -> str:
    text = unescape(text or "")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^(abstract|summary)\s*[:.]?\s*", "", text, flags=re.I)
    return clean_text(text)


def _abstract_from_meta(soup: BeautifulSoup) -> str:
    for name in ABSTRACT_META_NAMES:
        tag = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": name})
        if tag and tag.get("content"):
            abstract = _clean_abstract(tag["content"])
            if _looks_like_abstract(abstract):
                return abstract
    return ""


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

        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            abstract = item.get("abstract") or item.get("description")
            if isinstance(abstract, list):
                abstract = " ".join(str(x) for x in abstract)
            if abstract:
                abstract = _clean_abstract(str(abstract))
                if _looks_like_abstract(abstract):
                    return abstract
    return ""


def _abstract_from_visible_page(soup: BeautifulSoup) -> str:
    for selector in ABSTRACT_SELECTORS:
        tag = soup.select_one(selector)
        if not tag:
            continue
        text = _clean_abstract(tag.get_text(" ", strip=True))
        if _looks_like_abstract(text):
            return text

    for heading in soup.find_all(["h1", "h2", "h3", "h4", "strong"]):
        heading_text = heading.get_text(" ", strip=True).lower()
        if heading_text not in {"abstract", "summary"}:
            continue

        parts = []
        for sibling in heading.find_all_next(limit=8):
            if sibling.name in ["h1", "h2", "h3"] and sibling is not heading:
                break
            txt = sibling.get_text(" ", strip=True)
            if txt:
                parts.append(txt)

        text = _clean_abstract(" ".join(parts))
        if _looks_like_abstract(text):
            return text

    return ""


def fetch_abstract_from_article_page(url: str, timeout: int = 20) -> str:
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        return ""

    try:
        response = _session().get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
    except Exception as exc:
        print(f"[Abstract fallback] Could not open {url}: {exc}")
        return ""

    content_type = response.headers.get("content-type", "").lower()
    if "html" not in content_type and "xml" not in content_type:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    abstract = (
        _abstract_from_meta(soup)
        or _abstract_from_jsonld(soup)
        or _abstract_from_visible_page(soup)
    )

    if abstract:
        domain = urlparse(response.url).netloc
        print(f"[Abstract fallback] Found abstract from {domain}")
        time.sleep(0.7)
        return abstract

    time.sleep(0.7)
    return ""


def enrich_missing_abstract(paper: dict[str, Any]) -> dict[str, Any]:
    if clean_text(paper.get("abstract", "")):
        return paper

    url = clean_text(paper.get("url", ""))
    if not url:
        return paper

    abstract = fetch_abstract_from_article_page(url)
    if abstract:
        paper = dict(paper)
        paper["abstract"] = abstract
        paper["source"] = clean_text(paper.get("source", "")) + "+web_abstract"

    return paper
