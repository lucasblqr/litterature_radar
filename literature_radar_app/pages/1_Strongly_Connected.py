from src.app_helpers import render_interest_page

render_interest_page(
    page_key="strong",
    title="Strongly connected to Nikkil's group",
    description=(
        "Highest-priority papers across all selected journals: preventive care, health behavior, hypertension, "
        "adherence, provider and patient behavior, health systems, LMICs, aging, demography, and intervention evidence."
    ),
    score_col="score_strong",
    min_score_key="strong_min_score",
    allowed_journal_groups=None,
    pills=[("all selected journals", "blue"), ("highest priority", "green"), ("Nikkil profile", "orange")],
)
