from src.app_helpers import render_interest_page

render_interest_page(
    page_key="random",
    title="More random but interesting papers",
    description=(
        "Adjacent papers ranked by broader interests. This page is restricted mainly to broad science venues "
        "such as Nature, Science, Science Advances, Nature Human Behaviour, and PNAS."
    ),
    score_col="score_random",
    min_score_key="random_min_score",
    allowed_journal_groups=[
        "broad_science",
    ],
    pills=[("broad science venues", "purple"), ("adjacent ideas", "blue"), ("behavior / demography / AI", "green")],
)
