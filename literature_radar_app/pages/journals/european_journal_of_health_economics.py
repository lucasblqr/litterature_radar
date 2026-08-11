from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.journal_pages import render_single_journal_page


render_single_journal_page(
    title='European Journal of Health Economics',
    journal_names=['European Journal of Health Economics'],
    key_prefix='european_journal_of_health_economics',
)
