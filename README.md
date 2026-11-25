# FinTrust 360 — Consumer Complaint Analysis

## Project Overview

FinTrust 360 analyzes **5,000** consumer financial complaint records (`2025-10-01` to `2026-10-15`) across products, issue categories, submission channels, states, and financial institutions. The project covers end-to-end data cleaning in Python, exploratory and operational KPI queries in MySQL, Power BI DAX modeling, and an executive PDF report summarizing key findings, evidence-based recommendations, and analytical limitations.

After removing **25** exact duplicate records, the cleaned dataset contains **4,975** complaints (**4,665 Closed**, **310 Open**). All **310 Open** complaints have blank `date_company_responded`, `timely_response`, and `response_days` and are excluded from timely-response rate and average turnaround calculations.

---

## Folder Structure

```text
FinTrust-360/
├── Dataset/
│   ├── FinTrust_Cleaned.csv        # Cleaned dataset (4,975 rows, 16 columns)
│   ├── FinTrust_Cleaned.xlsx       # Cleaned workbook with 8 audit & summary sheets
│   └── lecture-file.csv            # Working source CSV read by clean_fintrust.py
├── Original/
│   └── lecture-file.csv            # Preserved untouched copy of the original CSV
├── PowerBI/
│   ├── FinTrust360_Dashboard.pbix  # Power BI Desktop dashboard file
│   └── measures.dax                # DateTable DAX script and 5 documented KPI measures
├── Report/
│   └── FinTrust_Analysis.pdf       # 3-page executive analysis report (PDF)
├── Screenshots/                    # Target folder for dashboard screenshot (dashboard.png)
├── Scripts/
│   └── clean_fintrust.py           # Python data cleaning, auditing, and export script
├── SQL/
│   └── Analysis.sql                # 10 commented MySQL analysis queries
├── AI_USAGE.md                     # Honest log of AI assistance, prompts, and verification
└── README.md                       # Project documentation
```

---

## Tools Used

- **Python** (`pandas`, `openpyxl`): Data auditing, deduplication, whitespace/case standardization, date validation, feature engineering (`state_missing_flag`, `response_days`), and Excel/CSV export.
- **MySQL**: Analytical SQL queries for executive KPIs, monthly trends, product/issue/channel/state breakdowns, turnaround stats, and overdue Open complaint tracking.
- **Power BI Desktop (DAX)**: Calendar table (`DateTable`) and KPI measures (`PowerBI/measures.dax`) for interactive dashboard reporting.
- **Microsoft Edge (Headless Print-to-PDF)**: Generating `Report/FinTrust_Analysis.pdf` from HTML/CSS.

---

## How to Run the Cleaning Script

### Prerequisites
- Python 3.10+ with `pandas` and `openpyxl` installed:
  ```powershell
  pip install pandas openpyxl
  ```

### Execution
Run from inside `FinTrust-360/`:

```powershell
python Scripts/clean_fintrust.py
```

The script reads `Dataset/lecture-file.csv` without modifying it and regenerates:
- `Dataset/FinTrust_Cleaned.csv` (`4,975` rows, `16` columns)
- `Dataset/FinTrust_Cleaned.xlsx` with 8 sheets: `Cleaned_Data`, `Cleaning_Log`, `Missing_Values`, `Duplicate_Records`, `Data_Quality_Summary`, `Category_Analysis`, `Product_Analysis`, and `Response_Analysis`.

---

## How to Run the SQL File

1. Create the `fintrust360` schema in MySQL and import `Dataset/FinTrust_Cleaned.csv` into a table named `complaints` with column headers matching the CSV (ensure empty fields in `date_company_responded`, `timely_response`, and `response_days` are stored as `NULL`).
2. Run `SQL/Analysis.sql` from the `FinTrust-360/` directory using the MySQL CLI:
   ```powershell
   mysql -u root -p < SQL/Analysis.sql
   ```
   Or open `SQL/Analysis.sql` in **MySQL Workbench** and execute the script.

> **Note:** Query 10 uses the fixed reference date `'2026-11-25'` (replacing `CURRENT_DATE()`) to list overdue `Open` complaints consistently with the report date.

---

## How to Open the Report & Dashboard

- **Executive PDF Report**: Open `Report/FinTrust_Analysis.pdf` in any PDF viewer or browser.
- **Power BI Dashboard**: Open `PowerBI/FinTrust360_Dashboard.pbix` in **Power BI Desktop**, and refer to `PowerBI/measures.dax` for the `DateTable` definition and 5 KPI measures (`Total Complaints`, `Open Complaints`, `Closed Complaints`, `Timely Response Rate`, and `Avg Response Time`).

---

## Key Results

| Metric | Value | Notes |
| --- | --- | --- |
| Original source rows | `5,000` | `Original/lecture-file.csv` |
| Exact duplicates removed | `25` | Archived in `Duplicate_Records` sheet |
| Cleaned dataset rows | `4,975` | `4,665` Closed (`93.77%`), `310` Open (`6.23%`) |
| Missing `state` values handled | `49` | Filled with `"Unknown"`; flagged in `state_missing_flag` |
| Closed-only Timely Response Rate | `90.08%` | `4,202` timely out of `4,665` Closed (`310` Open excluded) |
| Closed-only Avg Response Time | `8.76 days` | Range `1`–`25` days (`310` Open excluded) |
| Top Financial Product | `Credit card` | `1,191` complaints (`23.94%`), followed by `Checking or savings account` (`1,054`, `21.19%`) |
| Top Issue Category | `Unexpected fees` | `545` complaints (`10.95%`), spanning Credit card (`289`) & Checking/savings (`256`) |
| Lowest Product Timely Rate | `Mortgage` | `81.18%` timely, `9.76` avg days |
| Company Timely Rate Range | `81.80%`–`94.14%` | `Atlas Consumer Finance` (`81.80%`) and `Cedar Finance` (`81.91%`) trail the other 6 firms (`90.97%`–`94.14%`) |
| Overdue Open Complaints | `310` | All Open cases past due as of `2026-11-25` (`26`–`399` days overdue; mean `210.27` days) |

