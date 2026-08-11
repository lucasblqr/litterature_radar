from src.app_helpers import render_interest_page

render_interest_page(
    page_key="preventive",
    title="Preventive care",
    description=(
        "Papers across all selected journals related to preventive care, screening, early detection, primary care, "
        "community health workers, health services, adherence, follow-up, and preventive interventions."
    ),
    score_col="score_preventive",
    min_score_key="preventive_min_score",
    allowed_journal_groups=None,
    pills=[("all selected journals", "blue"), ("preventive care", "green"), ("screening / follow-up", "orange")],
    default_min_override=20,
    default_days=180,
)
