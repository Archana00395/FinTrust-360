# AI_USAGE.md

Project: CommerceIQ 360 – E-Commerce Delivery & Customer Experience Analytics

## Tools used
- Claude (Anthropic) – planning, data profiling, drafting SQL / DAX, explaining concepts
- Antigravity (Google agent IDE) – running the cleaning script and file tasks

## How AI helped

| Area | What AI did | What I did |
|---|---|---|
| Understanding the brief | Explained the task structure and the KPI traps (distinct order IDs, one review per order, delivered-sales formula) | Read the brief myself and wrote the KPI definitions in the README |
| Data cleaning | Profiled the CSV and suggested cleaning rules (duplicates, label trimming, region fill from city) | [Describe: ran the script, reviewed the log, tested in Excel] |
| SQL | Drafted the first version of the 9 queries | [Describe: ran each query, compared totals, fixed/edited queries] |
| Power BI | Suggested DAX measures and a page layout | [Describe: built the report, tested measures, formatted visuals] |
| Analysis | Helped structure findings and recommendations | [Describe: wrote the final findings in my own words from my results] |

## How I verified the output

- Opened the raw CSV in Excel and confirmed 5,000 rows, and found the duplicate rows with Remove Duplicates (25 found).
- Checked category and payment labels with filters after cleaning (7 categories, 4 payment methods).
- Counted blanks with COUNTBLANK (0 missing regions, 30 missing cities).
- Ran every SQL query and compared the results with the cleaned data:
  - 3,599 total orders, 3,430 delivered orders
  - Delivered sales about $676,669
  - Average rating about 3.94, based on one review per order
- Checked that Power BI KPI cards match the SQL results.
- [Add anything else you actually checked.]

## Where AI output was wrong or needed changing

- [Write real examples here, e.g. a query that double-counted reviews, a wrong column name, a DAX measure that needed fixing.]

## Responsibility
All AI-generated code and text was reviewed by me before use. The final analysis, recommendations and conclusions reflect my own understanding of the results.