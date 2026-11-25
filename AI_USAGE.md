# AI Usage & Verification Log

This document records exactly how AI assistance was used on the **FinTrust 360** project, what prompts were given, which verification checks were actually executed, and which steps remain pending manual execution outside this environment.

---

## 1. Tasks AI Helped With (and Current Status)

| Area | What AI Actually Did | Status |
| --- | --- | --- |
| **Workspace Organization** | Renamed `PowerBI/FinTrust360_Dashboard.pbix.pbix` to `PowerBI/FinTrust360_Dashboard.pbix`, created `Original/`, and copied `Dataset/lecture-file.csv` to `Original/lecture-file.csv` while keeping `Dataset/lecture-file.csv` intact. | Completed |
| **Cleaning Script (`Scripts/clean_fintrust.py`)** | Added `state_missing_flag` and filled missing `state` with `"Unknown"`, added nullable integer `response_days` (`date_company_responded - date_received`, blank for `Open`), added the `Cleaning_Log` worksheet (`step`, `issue found`, `rows affected`, `action taken`, `rationale`), added CSV export (`Dataset/FinTrust_Cleaned.csv`), updated `Data_Quality_Summary`, and ran the script to regenerate both cleaned files. | Completed & Verified |
| **SQL Comments & Reference Date (`SQL/Analysis.sql`)** | Added comments above all 10 queries explaining the business question, query behavior, and Open complaint exclusions/handling; replaced `CURRENT_DATE()` with `'2026-11-25'` in Query 10 without altering other query logic. | Edits Completed (MySQL execution blocked — see Section 4) |
| **Power BI DAX (`PowerBI/measures.dax`)** | Wrote `DateTable` and the 5 commented measures (`Total Complaints`, `Open Complaints`, `Closed Complaints`, `Timely Response Rate`, `Avg Response Time`) for table `FinTrust_Cleaned`. | DAX File Created (Power BI Desktop GUI steps pending — see Section 4) |
| **Analysis Report (`Report/FinTrust_Analysis.pdf`)** | Computed all metrics directly from `Dataset/FinTrust_Cleaned.csv` via Python, drafted 5 findings, 3 recommendations, and limitations, rendered a 3-page PDF via headless Microsoft Edge, and visually inspected all pages. | Completed (dashboard screenshot pending) |
| **Documentation (`README.md`, `AI_USAGE.md`)** | Authored project overview, run instructions, results summary, and this transparent AI usage log. | Completed |

---

## 2. Prompts Used

The following instructions were issued to the AI assistant during the session:

1. **Workspace cleanup**: Rename `PowerBI/FinTrust360_Dashboard.pbix.pbix` to `FinTrust360_Dashboard.pbix`, create `Original/`, and copy `lecture-file.csv` there alongside the cleaned file.
2. **Data cleaning updates**: Edit `Scripts/clean_fintrust.py` to fill missing `state` with `"Unknown"`, add `state_missing_flag` and `response_days` (blank for `Open`), add a `Cleaning_Log` sheet covering duplicates, whitespace/case fixes, missing states, date validation, and Open blank response fields, regenerate `.xlsx` and `.csv`, and verify row/status counts (`4,975` total, `4,665` Closed, `310` Open).
3. **Number check**: Compare printed cleaning and summary numbers against target figures before proceeding.
4. **SQL documentation & execution**: Add comments above each query in `SQL/Analysis.sql` (business question, query summary, Open complaint exclusions), replace `CURRENT_DATE()` with `'2026-11-25'` in Query 10, keep at least 8 queries without changing logic, and test in MySQL.
5. **Power BI DAX & dashboard build**: Create `PowerBI/measures.dax` (`Total Complaints`, `Open Complaints`, `Closed Complaints`, `Timely Response Rate`, `Avg Response Time`, `DateTable`) with comments, plus instructions/actions for building the dashboard and saving `Screenshots/dashboard.png`.
6. **PDF executive report**: Read `Dataset/FinTrust_Cleaned.csv` and `SQL/Analysis.sql`, build `Report/FinTrust_Analysis.pdf` with 5 findings, 3 recommendations, and required limitations, read the PDF back, and check at least three numbers against Power BI.
7. **Project documentation**: Write `README.md` and an honest `AI_USAGE.md`.

---

## 3. Verification Checks Actually Run

All checks below were executed directly and their outputs observed in this session:

1. **File Structure & Rename Verification** (PowerShell `Get-ChildItem`):
   - Verified `PowerBI/FinTrust360_Dashboard.pbix` (`182,362` bytes), `Original/lecture-file.csv` (`1,078,716` bytes), and `Dataset/lecture-file.csv` (`1,078,716` bytes).
2. **Cleaning Script Execution & Output Validation** (`python Scripts/clean_fintrust.py` + pandas/openpyxl verification on Python `3.14.3`, `pandas 3.0.6`, `openpyxl 3.1.5`):
   - Confirmed `5,000` source rows → `4,975` final rows (`25` exact duplicates removed).
   - Confirmed status breakdown: `4,665` Closed, `310` Open.
   - Confirmed `49` rows have `state == "Unknown"` and `state_missing_flag == True` (`0` remaining missing values in `state`).
   - Confirmed `response_days` has `4,665` non-null integer values for Closed rows and `0` non-null values (`310` blanks) for Open rows.
   - Confirmed `financial_product` (`26` fixes) and `submission_channel` (`17` fixes) standardization counts.
   - Verified all 8 sheets in `Dataset/FinTrust_Cleaned.xlsx` (`Cleaned_Data`, `Cleaning_Log`, `Missing_Values`, `Duplicate_Records`, `Data_Quality_Summary`, `Category_Analysis`, `Product_Analysis`, `Response_Analysis`) and inspected every row of `Cleaning_Log` and `Data_Quality_Summary`.
3. **Python Replication of SQL & DAX Metrics** (pandas queries on `Dataset/FinTrust_Cleaned.csv`):
   - Verified `Total Complaints = 4,975`, `Closed Complaints = 4,665`, `Open Complaints = 310`, Closed-only `Timely Response Rate = 90.08%` (`4,202 / 4,665`), and Closed-only `Avg Response Time = 8.76` days (`1`–`25` days).
   - Computed all monthly (`2025-10` to `2026-10`), product, issue category, company, state (`17` states + `Unknown`), channel, company-response, and overdue Open (`310` cases, `26`–`399` days past due as of `2026-11-25`) breakdowns used in `Report/FinTrust_Analysis.pdf`.
4. **PDF Inspection & Manual Review** (direct PDF read/render review of `Report/FinTrust_Analysis.pdf`):
   - Inspected rendered page images and OCR text of all pages after generation.
   - Caught and fixed an awkward page break after Finding 5 and a shortened label (`"Checking or savings"` → `"Checking or savings account"`), then re-rendered and re-read the final 3-page PDF (`205,029` bytes) to verify formatting and numbers.

---

## 4. Honest Disclosure of What Was *Not* Verified / Remains Pending

- **Live MySQL Execution**: Running `SQL/Analysis.sql` against the local MySQL 8.4 server (`C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe`) failed at authentication (`ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: NO)`), with no saved `mysql_config_editor` login path. As a result, `SQL/Analysis.sql` has **not yet** been executed inside MySQL and no MySQL output screenshot was captured.
- **Live Power BI Desktop Build & Cross-Check**: Because AI has no Power BI Desktop GUI automation or screen-capture capability, `PowerBI/FinTrust360_Dashboard.pbix` has not yet been updated interactively in Power BI Desktop and `Screenshots/dashboard.png` does not exist yet. Therefore, the 5 KPI numbers in `Report/FinTrust_Analysis.pdf` were cross-checked against the DAX logic in `PowerBI/measures.dax` evaluated via Python on `Dataset/FinTrust_Cleaned.csv`, **not** against a rendered Power BI Desktop visual or screenshot.

