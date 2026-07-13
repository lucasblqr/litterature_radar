from __future__ import annotations

from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import DB_PATH


PEOPLE = ["nikkil", "anna", "lucas", "vasanthi", "michaela", "caterina"]


def table_columns(conn: sqlite3.Connection) -> set[str]:
    return {row[1] for row in conn.execute("PRAGMA table_info(papers)").fetchall()}


def main() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        cols = table_columns(conn)

        for person in PEOPLE:
            col = f"keep_{person}"

            if col not in cols:
                print(f"Adding {col}")
                conn.execute(f"ALTER TABLE papers ADD COLUMN {col} INTEGER DEFAULT 0")

        cols = table_columns(conn)

        for person in PEOPLE:
            col = f"note_{person}"

            if col not in cols:
                print(f"Adding {col}")
                conn.execute(f"ALTER TABLE papers ADD COLUMN {col} TEXT DEFAULT ''")

        conn.commit()

    print("Personal-list columns are ready.")


if __name__ == "__main__":
    main()
