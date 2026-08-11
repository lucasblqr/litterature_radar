from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pages" / "journals"


JOURNALS = {
    "bmj_global_health.py": {
        "title": "BMJ Global Health",
        "aliases": ["BMJ Global Health", "BMJ Glob Health"],
        "key": "bmj_global_health",
    },
    "the_lancet_global_health.py": {
        "title": "The Lancet Global Health",
        "aliases": ["The Lancet Global Health", "Lancet Global Health"],
        "key": "the_lancet_global_health",
    },
    "plos_medicine.py": {
        "title": "PLOS Medicine",
        "aliases": ["PLOS Medicine", "PLoS Medicine"],
        "key": "plos_medicine",
    },
    "social_science_medicine.py": {
        "title": "Social Science & Medicine",
        "aliases": ["Social Science & Medicine", "Social Science and Medicine"],
        "key": "social_science_medicine",
    },
    "jama.py": {
        "title": "JAMA",
        "aliases": ["JAMA"],
        "key": "jama",
    },
    "jama_network_open.py": {
        "title": "JAMA Network Open",
        "aliases": ["JAMA Network Open"],
        "key": "jama_network_open",
    },
    "bmj.py": {
        "title": "BMJ",
        "aliases": ["BMJ", "British Medical Journal"],
        "key": "bmj",
    },
    "the_lancet.py": {
        "title": "The Lancet",
        "aliases": ["The Lancet", "Lancet"],
        "key": "the_lancet",
    },
    "new_england_journal_of_medicine.py": {
        "title": "New England Journal of Medicine",
        "aliases": ["New England Journal of Medicine", "NEJM"],
        "key": "nejm",
    },
    "nature_medicine.py": {
        "title": "Nature Medicine",
        "aliases": ["Nature Medicine"],
        "key": "nature_medicine",
    },
    "nature.py": {
        "title": "Nature",
        "aliases": ["Nature"],
        "key": "nature",
    },
    "nature_human_behaviour.py": {
        "title": "Nature Human Behaviour",
        "aliases": ["Nature Human Behaviour", "Nature Human Behavior"],
        "key": "nature_human_behaviour",
    },
    "science.py": {
        "title": "Science",
        "aliases": ["Science"],
        "key": "science",
    },
    "science_advances.py": {
        "title": "Science Advances",
        "aliases": ["Science Advances"],
        "key": "science_advances",
    },
    "science_translational_medicine.py": {
        "title": "Science Translational Medicine",
        "aliases": ["Science Translational Medicine"],
        "key": "science_translational_medicine",
    },
    "pnas.py": {
        "title": "PNAS",
        "aliases": ["PNAS", "Proceedings of the National Academy of Sciences"],
        "key": "pnas",
    },
    "american_economic_review.py": {
        "title": "American Economic Review",
        "aliases": ["American Economic Review"],
        "key": "american_economic_review",
    },
    "quarterly_journal_of_economics.py": {
        "title": "Quarterly Journal of Economics",
        "aliases": ["Quarterly Journal of Economics"],
        "key": "quarterly_journal_of_economics",
    },
    "journal_of_political_economy.py": {
        "title": "Journal of Political Economy",
        "aliases": ["Journal of Political Economy"],
        "key": "journal_of_political_economy",
    },
    "econometrica.py": {
        "title": "Econometrica",
        "aliases": ["Econometrica"],
        "key": "econometrica",
    },
    "review_of_economics_and_statistics.py": {
        "title": "Review of Economics and Statistics",
        "aliases": ["Review of Economics and Statistics"],
        "key": "review_of_economics_and_statistics",
    },
    "aej_applied_economics.py": {
        "title": "AEJ: Applied Economics",
        "aliases": [
            "American Economic Journal: Applied Economics",
            "AEJ: Applied Economics",
        ],
        "key": "aej_applied_economics",
    },
    "aer_insights.py": {
        "title": "AER Insights",
        "aliases": ["AER Insights", "AER: Insights"],
        "key": "aer_insights",
    },
    "journal_of_development_economics.py": {
        "title": "Journal of Development Economics",
        "aliases": ["Journal of Development Economics"],
        "key": "journal_of_development_economics",
    },
    "journal_of_health_economics.py": {
        "title": "Journal of Health Economics",
        "aliases": ["Journal of Health Economics"],
        "key": "journal_of_health_economics",
    },
    "health_economics.py": {
        "title": "Health Economics",
        "aliases": ["Health Economics"],
        "key": "health_economics",
    },
    "american_journal_of_health_economics.py": {
        "title": "American Journal of Health Economics",
        "aliases": ["American Journal of Health Economics"],
        "key": "american_journal_of_health_economics",
    },
    "european_journal_of_health_economics.py": {
        "title": "European Journal of Health Economics",
        "aliases": ["European Journal of Health Economics"],
        "key": "european_journal_of_health_economics",
    },
}


TEMPLATE = '''from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.journal_pages import render_single_journal_page


render_single_journal_page(
    title={title!r},
    journal_names={aliases!r},
    key_prefix={key!r},
)
'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    for filename, info in JOURNALS.items():
        path = OUT / filename
        path.write_text(
            TEMPLATE.format(
                title=info["title"],
                aliases=info["aliases"],
                key=info["key"],
            ),
            encoding="utf-8",
        )
        print(f"Created {path}")

    print("Done. Journal subpages created.")


if __name__ == "__main__":
    main()
