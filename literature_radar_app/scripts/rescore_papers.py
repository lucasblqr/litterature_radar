from __future__ import annotations

from pathlib import Path
import sys
import sqlite3

ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORTS))

from src.config import DB_PATH, load_ranking_rules
from src.database import init_db, upsert_papers
from src.ranking import score_many


def main() -> None:
    init_db()
    rules = load_ranking_rules()

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM papers").fetchall()

    papers = [dict(row) for row in rows]
    scored = score_many(papers, rules)
    n = upsert_papers(scored)

    print(f"Recomputed scores for {n} papers.")


if __name__ == "__main__":
    main()
