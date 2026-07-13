from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.journal_pages import render_single_journal_page


render_single_journal_page(
    title='Review of Economics and Statistics',
    journal_names=['Review of Economics and Statistics'],
    key_prefix='review_of_economics_and_statistics',
)
