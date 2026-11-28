# AI_USAGE.md

Project: **FinTrust 360 – Financial Customer Complaints & Response Analytics**

## Permission
The internship company told me I could use AI assistance on this project. I am documenting it here.

## Tools used
- **Claude (Anthropic)**: reviewing my project against the brief, planning the remaining steps, explaining concepts.
- **Antigravity (Google agent IDE)**: editing and running the Python cleaning script, adding SQL comments, writing the DAX file, generating the PDF report, writing README/AI_USAGE drafts, git commands.

## How AI helped

| Area | What AI did | What I did |
|---|---|---|
| Data cleaning (`Scripts/clean_fintrust.py`) | Added `state_missing_flag`, `response_days`, the `Cleaning_Log` sheet and CSV export; ran the script | Built the original cleaning (25 duplicates removed, label standardisation, date checks) and reviewed the outputs |
| SQL (`SQL/Analysis.sql`) | Added explanatory comments to the 10 queries; replaced `CURRENT_DATE()` with `'2026-11-25'` | Wrote the original 10 queries |
| Power BI (`PowerBI/measures.dax`) | Wrote the DateTable and 5 KPI measures | [Fill in only what you actually did in Power BI Desktop] |
| Analysis report (`Report/FinTrust_Analysis.pdf`) | Computed figures from the cleaned CSV, drafted the findings and recommendations, rendered the PDF | Reviewed the text and numbers |
| Documentation | Drafted README and this file | Reviewed and corrected them |

## How the output was checked
- Row counts from the cleaned CSV: 5,000 source rows, 25 duplicates removed, 4,975 rows (4,665 Closed, 310 Open).
- Timely response rate (90.08%, 4,202 of 4,665) and average response time (8.76 days) recomputed in Python on Closed complaints only.
- Cleaned workbook sheets and the Cleaning_Log opened and read.

## Not yet done / limitations
- [Edit this section to match reality before submitting.] The SQL file has not been executed against a MySQL database, and the Power BI report has not been fully built and cross-checked against the PDF figures.

## Where AI output needed correcting
- An earlier version of this file was a template from a different project (CommerceIQ 360) and described checks I had not run. It was replaced with this version.

## Responsibility
I reviewed the AI-assisted work before submitting it, and I am responsible for what is in this repository.