from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORTS))

from src.collectors import collect_all
from src.config import load_journals, load_ranking_rules
from src.database import upsert_papers
from src.ranking import score_many


ECON_GROUPS = {
    "health_econ_journals",
    "top_econ_journals",
    "applied_development_econ",
    "econ_top",
    "econ_field",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=365, help="Number of days back to collect Econ journals.")
    args = parser.parse_args()

    journals = [journal for journal in load_journals() if journal.get("group") in ECON_GROUPS]
    rules = load_ranking_rules()

    papers = collect_all(journals, days=args.days)
    scored = score_many(papers, rules)
    n = upsert_papers(scored)

    print(f"Collected and stored {n} Econ-journal papers from the last {args.days} days.")


if __name__ == "__main__":
    main()
