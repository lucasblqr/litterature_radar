from src.app_helpers import render_interest_page

render_interest_page(
    page_key="hypertension",
    title="Hypertension",
    description=(
        "Papers across all selected journals related to hypertension, blood pressure, cardiovascular disease, NCDs, "
        "screening, treatment, adherence, primary care, and care cascades."
    ),
    score_col="score_hypertension",
    min_score_key="hypertension_min_score",
    allowed_journal_groups=None,
    pills=[("all selected journals", "blue"), ("hypertension", "green"), ("CVD / NCDs", "orange")],
    default_min_override=20,
    default_days=180,
)
