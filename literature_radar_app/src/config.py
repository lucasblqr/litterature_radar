from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "papers.db"


def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_journals() -> list[dict[str, Any]]:
    cfg = load_yaml(DATA_DIR / "journals.yml")
    return cfg.get("journals", [])


def load_ranking_rules() -> dict[str, Any]:
    return load_yaml(DATA_DIR / "ranking_rules.yml")
