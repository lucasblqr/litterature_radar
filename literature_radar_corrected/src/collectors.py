from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from typing import Any

import requests

from .abstract_fetcher import enrich_missing_abstract
from .utils import clean_text, journal_matches, make_unique_key, parse_date, safe_date_from_parts


CROSSREF_URL = "https://api.crossref.org/works"
PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
PUBMED_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def _article_url(url: str | None = "", doi: str | None = "", pmid: str | None = "") -> str:
    url = (url or "").strip()
    doi = (doi or "").strip()
    pmid = (pmid or "").strip()

    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("www."):
        return "https://" + url
    if doi:
        doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
        return f"https://doi.org/{doi}"
    if pmid:
        return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    return ""


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": "LiteratureRadar/0.1 (mailto:replace-with-your-email@example.com)",
        }
    )
    return s


def _authors_from_crossref(item: dict[str, Any]) -> str:
    authors = []
    for a in item.get("author", [])[:8]:
        given = a.get("given", "")
        family = a.get("family", "")
        name = " ".join([given, family]).strip()
        if name:
            authors.append(name)
    if len(item.get("author", [])) > 8:
        authors.append("et al.")
    return ", ".join(authors)


def _published_date_from_crossref(item: dict[str, Any]) -> str | None:
    for key in ["published-print", "published-online", "published", "issued", "created"]:
        if key in item and "date-parts" in item[key]:
            val = safe_date_from_parts(item[key]["date-parts"])
            if val:
                return val
    return None


def _extract_crossref_item(item: dict[str, Any], journal: dict[str, Any]) -> dict[str, Any] | None:
    title = clean_text(item.get("title", [""])[0] if item.get("title") else "")
    if not title:
        return None

    containers = item.get("container-title") or []
    journal_name = clean_text(containers[0]) if containers else journal.get("name", "")
    if containers and not any(journal_matches(c, journal) for c in containers):
        return None

    doi = clean_text(item.get("DOI", ""))
    url = _article_url(clean_text(item.get("URL", "")), doi=doi)
    published_date = _published_date_from_crossref(item)

    return {
        "unique_key": make_unique_key(doi, title, journal_name),
        "title": title,
        "journal": journal_name,
        "configured_journal": journal.get("short_name") or journal.get("name"),
        "journal_group": journal.get("group", ""),
        "source": "crossref",
        "doi": doi,
        "url": url,
        "published_date": published_date,
        "authors": _authors_from_crossref(item),
        "abstract": clean_text(item.get("abstract", "")),
        "fetched_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
    }


def fetch_crossref(journal: dict[str, Any], start: date, end: date, rows: int = 200) -> list[dict[str, Any]]:
    params = {
        "query.container-title": journal.get("name", ""),
        "filter": f"from-pub-date:{start.isoformat()},until-pub-date:{end.isoformat()},type:journal-article",
        "sort": "published",
        "order": "desc",
        "rows": rows,
        "select": "DOI,title,container-title,published-print,published-online,published,issued,created,URL,author,abstract,type",
    }

    try:
        r = _session().get(CROSSREF_URL, params=params, timeout=30)
        r.raise_for_status()
        items = r.json().get("message", {}).get("items", [])
    except Exception as exc:
        print(f"[Crossref] {journal.get('name')}: {exc}")
        return []

    papers = []
    for item in items:
        paper = _extract_crossref_item(item, journal)
        if paper:
            papers.append(paper)

    time.sleep(0.2)
    return papers


def _doi_from_pubmed(summary: dict[str, Any]) -> str:
    for article_id in summary.get("articleids", []):
        if article_id.get("idtype") == "doi":
            return clean_text(article_id.get("value", ""))
    return ""


def _authors_from_pubmed(summary: dict[str, Any]) -> str:
    authors = []
    for a in summary.get("authors", [])[:8]:
        name = clean_text(a.get("name", ""))
        if name:
            authors.append(name)
    if len(summary.get("authors", [])) > 8:
        authors.append("et al.")
    return ", ".join(authors)


def _abstracts_from_pubmed(ids: list[str], session: requests.Session) -> dict[str, str]:
    ids = [str(x) for x in ids if str(x).strip()]
    if not ids:
        return {}

    try:
        r = session.get(
            PUBMED_EFETCH_URL,
            params={"db": "pubmed", "id": ",".join(ids), "retmode": "xml"},
            timeout=30,
        )
        r.raise_for_status()
        root = ET.fromstring(r.content)
    except Exception as exc:
        print(f"[PubMed abstract fetch] {exc}")
        return {}

    abstracts: dict[str, str] = {}
    for article in root.findall(".//PubmedArticle"):
        pmid_el = article.find(".//MedlineCitation/PMID")
        if pmid_el is None or not pmid_el.text:
            continue

        pmid = pmid_el.text.strip()
        parts: list[str] = []

        for node in article.findall(".//Abstract/AbstractText"):
            label = clean_text(node.attrib.get("Label", ""))
            text = clean_text(" ".join(node.itertext()))
            if text:
                parts.append(f"{label}: {text}" if label else text)

        for node in article.findall(".//OtherAbstract/AbstractText"):
            label = clean_text(node.attrib.get("Label", ""))
            text = clean_text(" ".join(node.itertext()))
            if text:
                parts.append(f"{label}: {text}" if label else text)

        abstract = clean_text(" ".join(parts))
        if abstract:
            abstracts[pmid] = abstract

    return abstracts


def _pubmed_journal_query(journal: dict[str, Any]) -> str:
    journal_terms = [journal.get("name", "")]
    journal_terms.extend(journal.get("aliases", []) or [])
    if journal.get("short_name"):
        journal_terms.append(journal["short_name"])

    parts: list[str] = []
    seen: set[str] = set()
    for term in journal_terms:
        term = clean_text(term)
        if not term or term.lower() in seen:
            continue
        seen.add(term.lower())
        parts.append(f'"{term}"[Journal]')
        parts.append(f'"{term}"[TA]')
    return " OR ".join(parts)


def fetch_pubmed(journal: dict[str, Any], start: date, end: date, retmax: int = 200) -> list[dict[str, Any]]:
    journal_query = _pubmed_journal_query(journal)
    if not journal_query:
        return []

    term = (
        f"({journal_query}) AND "
        f"({start.strftime('%Y/%m/%d')}[Date - Publication] : "
        f"{end.strftime('%Y/%m/%d')}[Date - Publication])"
    )
    search_params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": retmax,
        "sort": "pub date",
    }

    try:
        s = _session()
        r = s.get(PUBMED_ESEARCH_URL, params=search_params, timeout=30)
        r.raise_for_status()
        ids = r.json().get("esearchresult", {}).get("idlist", [])
    except Exception as exc:
        print(f"[PubMed search] {journal.get('name')}: {exc}")
        return []

    if not ids:
        time.sleep(0.2)
        return []

    try:
        summary_params = {"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
        r = s.get(PUBMED_ESUMMARY_URL, params=summary_params, timeout=30)
        r.raise_for_status()
        data = r.json().get("result", {})
    except Exception as exc:
        print(f"[PubMed summary] {journal.get('name')}: {exc}")
        return []

    abstracts_by_pmid = _abstracts_from_pubmed(ids, s)
    papers = []
    for pmid in ids:
        item = data.get(pmid)
        if not item:
            continue

        title = clean_text(item.get("title", ""))
        if not title:
            continue

        journal_name = clean_text(item.get("fulljournalname", "")) or journal.get("name", "")
        doi = _doi_from_pubmed(item)
        pubdate = parse_date(item.get("pubdate", ""))

        papers.append(
            {
                "unique_key": make_unique_key(doi, title, journal_name),
                "title": title,
                "journal": journal_name,
                "configured_journal": journal.get("short_name") or journal.get("name"),
                "journal_group": journal.get("group", ""),
                "source": "pubmed",
                "doi": doi,
                "url": _article_url(doi=doi, pmid=pmid),
                "published_date": pubdate.isoformat() if pubdate else None,
                "authors": _authors_from_pubmed(item),
                "abstract": abstracts_by_pmid.get(str(pmid), ""),
                "fetched_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            }
        )

    time.sleep(0.2)
    return papers


def collect_for_journal(journal: dict[str, Any], start: date, end: date) -> list[dict[str, Any]]:
    papers = []
    sources = journal.get("sources", ["crossref"])

    if "pubmed" in sources:
        papers.extend(fetch_pubmed(journal, start, end))
    if "crossref" in sources:
        papers.extend(fetch_crossref(journal, start, end))

    deduped: dict[str, dict[str, Any]] = {}
    for paper in papers:
        if not paper.get("published_date"):
            continue

        key = paper["unique_key"]
        if key not in deduped:
            deduped[key] = paper
            continue

        old = deduped[key]
        if not old.get("abstract") and paper.get("abstract"):
            deduped[key] = paper
        elif old.get("source") == "crossref" and paper.get("source") == "pubmed" and paper.get("abstract"):
            deduped[key] = paper

    enriched = []
    for paper in deduped.values():
        enriched.append(enrich_missing_abstract(paper))

    return enriched


def collect_all(journals: list[dict[str, Any]], days: int = 25) -> list[dict[str, Any]]:
    end = date.today()
    start = end - timedelta(days=days)
    all_papers = []

    for journal in journals:
        print(f"Collecting: {journal.get('short_name') or journal.get('name')}")
        all_papers.extend(collect_for_journal(journal, start, end))

    deduped: dict[str, dict[str, Any]] = {}
    for paper in all_papers:
        key = paper["unique_key"]
        if key not in deduped:
            deduped[key] = paper
            continue

        old = deduped[key]
        if not old.get("abstract") and paper.get("abstract"):
            deduped[key] = paper

    return list(deduped.values())
