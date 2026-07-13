from src.app_helpers import render_interest_page

render_interest_page(
    page_key="health",
    title="Health papers related to our work",
    description=(
        "Interest-based ranking, but restricted to health and medical publication venues only: medical/global health journals, "
        "Nature Medicine, and Science Translational Medicine."
    ),
    score_col="score_health",
    min_score_key="health_min_score",
    allowed_journal_groups=[
        "medical_global_health",
        "medical_broad_science",
    ],
    pills=[("health journals only", "green"), ("clinical/global health", "blue"), ("Nature Med / STM", "orange")],
)
