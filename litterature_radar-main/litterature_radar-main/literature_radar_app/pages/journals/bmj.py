from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.journal_pages import render_single_journal_page


render_single_journal_page(
    title='BMJ',
    journal_names=['BMJ', 'British Medical Journal'],
    key_prefix='bmj',
)
