from __future__ import annotations

import json
from typing import Any

from .utils import clean_text, normalize


SCORE_COLUMNS = {
    "strong": "score_strong",
    "econ": "score_econ",
    "health": "score_health",
    "random": "score_random",
    "preventive": "score_preventive",
    "hypertension": "score_hypertension",
    "mental_models": "score_mental_models",
}


def _keyword_hits(text_norm: str, terms: list[str]) -> list[str]:
    hits = []
    padded = f" {text_norm} "
    for term in terms:
        term_norm = normalize(term)
        if not term_norm:
            continue
        if f" {term_norm} " in padded or term_norm in text_norm:
            hits.append(term)
    return hits


def score_paper(paper: dict[str, Any], rules: dict[str, Any]) -> dict[str, Any]:
    text = " ".join(
        [
            clean_text(paper.get("title")),
            clean_text(paper.get("abstract")),
            clean_text(paper.get("journal")),
        ]
    )
    text_norm = normalize(text)
    group = paper.get("journal_group", "")

    negative_cfg = rules.get("negative_keywords", {}).get("general", {})
    negative_hits = _keyword_hits(text_norm, negative_cfg.get("terms", []))
    negative_penalty = int(negative_cfg.get("weight", -10)) * len(negative_hits)

    for category, cfg in rules.get("categories", {}).items():
        score = 0
        reasons = []

        bonus = rules.get("journal_group_bonus", {}).get(category, {}).get(group, 0)
        if bonus:
            score += int(bonus)
            reasons.append(f"journal group: +{bonus}")

        for level in ["high", "medium", "low"]:
            hits = _keyword_hits(text_norm, cfg.get(level, []))
            weight = int(cfg.get(f"{level}_weight", 0))
            if hits and weight:
                score += weight * len(hits)
                sample = ", ".join(hits[:5])
                if len(hits) > 5:
                    sample += ", ..."
                reasons.append(f"{level} keywords: {sample}")

        if negative_hits:
            score += negative_penalty
            reasons.append("negative keywords: " + ", ".join(negative_hits[:5]))

        score = max(0, int(score))
        paper[f"score_{category}"] = score
        paper[f"reasons_{category}"] = reasons

    return paper


def score_many(papers: list[dict[str, Any]], rules: dict[str, Any]) -> list[dict[str, Any]]:
    return [score_paper(paper, rules) for paper in papers]
