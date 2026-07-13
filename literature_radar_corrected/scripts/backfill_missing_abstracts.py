from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORTS))

from src.abstract_fetcher import enrich_missing_abstract
from src.config import DB_PATH, load_ranking_rules
from src.database import init_db, upsert_papers
from src.ranking import score_many


TARGET_SQL = """
SELECT *
FROM papers
WHERE COALESCE(TRIM(abstract), '') = ''
  AND (
    LOWER(journal) LIKE '%bmj global health%'
    OR LOWER(journal) LIKE '%bmj glob health%'
    OR LOWER(configured_journal) LIKE '%bmj global health%'
    OR LOWER(journal) LIKE '%lancet%global%health%'
    OR LOWER(configured_journal) LIKE '%lancet%global%health%'
    OR LOWER(url) LIKE '%gh.bmj.com%'
    OR LOWER(url) LIKE '%/journals/langlo/%'
  )
ORDER BY published_date DESC
LIMIT ?
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50, help="Maximum papers to backfill in one run.")
    args = parser.parse_args()

    init_db()
    rules = load_ranking_rules()

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = [dict(row) for row in conn.execute(TARGET_SQL, (int(args.limit),)).fetchall()]

    if not rows:
        print("No missing BMJ Global Health or Lancet Global Health abstracts found.")
        return

    print(f"Trying to backfill abstracts for {len(rows)} papers...")
    enriched = []
    found = 0

    for row in rows:
        updated = enrich_missing_abstract(row)
        if (updated.get("abstract") or "").strip():
            found += 1
        enriched.append(updated)

    scored = score_many(enriched, rules)
    stored = upsert_papers(scored)
    print(f"Backfill finished. Found {found} abstracts. Updated {stored} database rows.")


if __name__ == "__main__":
    main()
