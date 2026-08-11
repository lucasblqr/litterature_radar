ECON JOURNAL 60-DAY COLLECTION FIX
==================================

What changed
------------
The economics journals are now collected from Crossref through their exact ISSN
journal endpoints instead of fuzzy journal-title searches.

The Econ Journal page itself still applies NO topic/ranking/keyword filter. It shows
papers in the configured Econ journals whose publication date falls in the last 60 days.

The Crossref collector also now prefers the online publication date when it is
available, before the print issue date.

Economics journals configured with exact ISSNs
-----------------------------------------------
American Economic Review
Quarterly Journal of Economics
Journal of Political Economy
Review of Economics and Statistics
Econometrica
American Economic Journal: Applied Economics
American Economic Review: Insights / AER: Insights
Journal of Development Economics
Journal of Health Economics
Health Economics
American Journal of Health Economics
The European Journal of Health Economics

Fastest way to refresh Econ only
--------------------------------
1. Make sure start_app.bat has been run at least once.
2. Run: update_econ_60_days.bat
3. Run: run_app.bat
4. Open Team's interest -> Econ Journal.

For future full updates, update_papers.bat also uses the exact ISSN logic for these
Economics journals.
