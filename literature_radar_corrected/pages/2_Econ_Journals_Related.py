from src.app_helpers import render_interest_page

render_interest_page(
    page_key="econ",
    title="Econ papers related to our work",
    description=(
        "Interest-based ranking, restricted to economics publication venues only. "
        "Because Econ journals publish fewer papers, this page shows a longer window by default and ranks papers by topic and method relevance."
    ),
    score_col="score_econ",
    min_score_key="econ_min_score",
    allowed_journal_groups=[
        "health_econ_journals",
        "top_econ_journals",
        "applied_development_econ",
    ],
    pills=[
        ("econ journals only", "blue"),
        ("365-day window", "green"),
        ("methods boosted", "purple"),
        ("health/development/demography", "orange"),
    ],
    default_min_override=0,
    default_days=365,
)
