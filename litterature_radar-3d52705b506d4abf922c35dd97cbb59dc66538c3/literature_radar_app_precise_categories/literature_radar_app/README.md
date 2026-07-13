# Literature Radar

A small Streamlit app to collect new papers from selected journals, rank them with transparent rules, and display them on separate pages:

1. Strongly connected to Nikkil's group
2. Health economics / development papers
3. Global health / preventive care papers
4. Adjacent interesting papers
5. All papers
6. Ranking rules

The app uses:
- Crossref for general DOI metadata
- PubMed / NCBI E-utilities for biomedical journals
- SQLite as a local database
- Streamlit as the dashboard

## First setup on Windows

1. Install Python from <https://www.python.org/downloads/>
2. Unzip this folder.
3. Double-click:

```text
start_app.bat
```

This creates the Python environment, installs packages, and opens the app. After the first time, you can also use `run_app.bat`.

The app should open in your browser.

## Manual update

To collect recent papers manually, double-click:

```text
update_papers.bat
```

Or run:

```bash
python scripts/update_papers.py --days 25
```

The first/manual update uses 60 days so that you quickly collect at least 100 papers. The scheduled update uses a 35-day window so that a twice-monthly update does not miss papers.

## Twice-monthly update

This project includes a GitHub Actions workflow:

```text
.github/workflows/update_papers.yml
```

It is scheduled for the 1st and 15th of every month at 06:00 UTC.

If you put this project in a GitHub repository, the workflow can update `papers.db` and the exported digest twice per month.

## Ranking rules

Edit:

```text
data/ranking_rules.yml
```

You can add keywords, change weights, and adjust minimum scores.

## Journal list

Edit:

```text
data/journals.yml
```

You can add or remove journals. For medical journals, keep `pubmed` as a source. For economics journals, `crossref` is usually enough.

## Important notes

This is an MVP. It is designed to be transparent and easy to modify.

Some publishers do not provide abstracts through Crossref. In those cases, the app ranks based on the title, journal, and available metadata. PubMed usually gives better metadata for medical papers, although abstracts are not used in this first version.

The app does not download paywalled articles. It only collects public metadata and links.

## Feedback checkboxes

The ranking pages include checkboxes for Nikkil, Anna, Caterina, Michaela, and Vasanthi. These are saved in the local SQLite database. For now they are feedback signals; in a later version they can be used to reweight the ranking rules.


## If Streamlit is missing

If you see:

```text
No module named streamlit
```

double-click:

```text
repair_environment.bat
```

This deletes the broken Python environment and reinstalls the packages.


## Ranking profile

This version is tuned for Prof. Nikkil Sudharsanan's group at TUM: behavioral science for disease prevention and health care, preventive health services, cardiovascular disease prevention, hypertension, adherence, provider and patient behavior, health messaging, health systems, population health, aging, demography, and LMIC settings such as India, Indonesia, and Cambodia.


## Interface

This version also includes a polished interface: cleaner home page, card-style navigation, softer colors, improved spacing, styled metrics, and clearer ranking pages.


## Links

Each ranking page now has two ways to open papers:

1. The `Link` column in the table.
2. A more reliable `Open selected paper` button below the table.

If the table link is not clickable in a browser, use the button.


## Readable layout and BibTeX

Ranking pages now have three display modes:

1. `Readable cards`: no horizontal scrolling, with title, journal, date, abstract, link, and BibTeX.
2. `Compact table`: a smaller table with the main fields only.
3. `BibTeX table`: ready-to-copy BibTeX entries.

Team feedback checkboxes are now in a separate compact table to avoid horizontal scrolling.


## Correct page logic

This version keeps the original interest-based categories, but journal groups are handled correctly:

1. Strongly connected to Nikkil's group: all selected journals, ranked by group relevance.
2. Econ papers related to our work: only economics publication venues.
3. Health papers related to our work: only health/medical publication venues.
4. More random but interesting papers: mainly broad science venues.

Within each page, papers are still ranked using the interest-specific scores.


## Clean restored version

This version restores the clean structure:

1. Strongly connected to Nikkil's group
2. Econ papers related to our work
3. Health papers related to our work
4. More random but interesting papers
5. All papers
6. Journal groups and rules

The only change is that the Econ page starts with minimum relevance score 0, so Econ-journal papers are not hidden by a strict threshold.


## More Econ papers, still ranked

The Econ page now has special behavior:

- It is still restricted to Econ publication venues.
- It shows a 365-day window by default.
- The minimum relevance threshold is 0 by default, so Econ papers are not hidden.
- Papers are ranked higher if they match health/development/demography topics or causal methods.

To fill the Econ page with enough papers, run:

```text
update_econ_papers.bat
```

This collects one year of papers from Econ journals only.


## New precise categories

This version adds three interest pages across all selected journals:

1. Preventive care
2. Hypertension
3. Mental models in health

After switching to this version, run:

```text
rescore_papers.bat
```

This recomputes the new category scores for papers already in the database. New updates will score these categories automatically.
