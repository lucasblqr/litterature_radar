from src.app_helpers import render_interest_page

render_interest_page(
    page_key="mental_models",
    title="Mental models in health",
    description=(
        "Papers across all selected journals related to mental models, belief change, misinformation, risk perception, "
        "health behavior change, trust, health communication, adherence behavior, and patient/provider decision-making."
    ),
    score_col="score_mental_models",
    min_score_key="mental_models_min_score",
    allowed_journal_groups=None,
    pills=[("all selected journals", "blue"), ("beliefs / behavior change", "purple"), ("health communication", "green")],
    default_min_override=18,
    default_days=180,
)
