from __future__ import annotations

from pathlib import Path
import sys

ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORTS))

import pandas as pd

from src.config import ROOT
from src.database import init_db, load_papers


EXPORTS = ROOT / "exports"
EXPORTS.mkdir(exist_ok=True)


def _format_section(title: str, df: pd.DataFrame, score_col: str) -> str:
    lines = [f"## {title}", ""]
    if df.empty:
        lines.append("No papers found.")
        lines.append("")
        return "\n".join(lines)

    for _, row in df.head(20).iterrows():
        score = row.get(score_col, "")
        date = row.get("published_date", "")
        journal = row.get("journal", "")
        paper_title = row.get("title", "")
        url = row.get("url", "")
        lines.append(f"- **{score}** | {date} | {journal} | [{paper_title}]({url})")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    init_db()
    sections = [
        ("Strongly connected to our work", "score_strong", 35),
        ("Economics papers related to our work", "score_econ", 25),
        ("Health / medical papers related to our work", "score_health", 25),
        ("Interesting but more random papers", "score_random", 20),
    ]

    chunks = ["# Literature Radar Digest", ""]
    all_export = []

    for title, score_col, min_score in sections:
        df = load_papers(score_col=score_col, min_score=min_score, days=30, limit=100)
        chunks.append(_format_section(title, df, score_col))
        if not df.empty:
            df = df.copy()
            df["section"] = title
            all_export.append(df)

    (EXPORTS / "latest_digest.md").write_text("\n".join(chunks), encoding="utf-8")

    if all_export:
        pd.concat(all_export, ignore_index=True).to_csv(EXPORTS / "papers_latest.csv", index=False)
    else:
        pd.DataFrame().to_csv(EXPORTS / "papers_latest.csv", index=False)

    print("Exported exports/latest_digest.md and exports/papers_latest.csv")


if __name__ == "__main__":
    main()
