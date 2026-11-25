USE fintrust360;

-- These queries assume the cleaned CSV is imported into a table named `complaints`,
-- with column names matching the CSV headers.

-- 1. Executive overview
-- Business Question: What are the overall complaint volume, resolution status split, timely-response rate, and average response turnaround?
-- What it does: Aggregates total rows, unique complaint IDs, Closed vs. Open counts, timely-response percentage, and average days to respond across the full dataset.
-- Open complaints handling: Open complaints are included in total and status counts, but excluded from timely_response_rate_pct and avg_days_to_respond because those columns are NULL for Open complaints (and AVG() ignores NULLs) since they are still awaiting a response.
SELECT
    COUNT(*) AS total_complaints,
    COUNT(DISTINCT complaint_id) AS unique_complaint_ids,
    SUM(CASE WHEN LOWER(TRIM(response_status)) = 'closed' THEN 1 ELSE 0 END) AS closed_complaints,
    SUM(CASE WHEN LOWER(TRIM(response_status)) = 'open' THEN 1 ELSE 0 END) AS open_complaints,
    ROUND(AVG(
        CASE
            WHEN LOWER(TRIM(timely_response)) = 'yes' THEN 100.0
            WHEN LOWER(TRIM(timely_response)) = 'no' THEN 0.0
            ELSE NULL
        END
    ), 2) AS timely_response_rate_pct,
    ROUND(AVG(
        CASE
            WHEN date_received IS NOT NULL AND date_company_responded IS NOT NULL
                THEN DATEDIFF(date_company_responded, date_received)
            ELSE NULL
        END
    ), 2) AS avg_days_to_respond
FROM complaints;

-- 2. Monthly complaint volume and timely-response rate
-- Business Question: How do complaint volumes, closed counts, and timely-response rates trend month over month?
-- What it does: Groups complaints with a non-null date_received by YYYY-MM month and calculates monthly complaint volume, closed complaints, and timely-response percentage.
-- Open complaints handling: Open complaints are included in monthly complaint_count, but excluded from timely_response_rate_pct because their timely_response is NULL (pending response) and AVG() ignores NULLs.
SELECT
    DATE_FORMAT(date_received, '%Y-%m') AS complaint_month,
    COUNT(*) AS complaint_count,
    SUM(CASE WHEN LOWER(TRIM(response_status)) = 'closed' THEN 1 ELSE 0 END) AS closed_complaints,
    ROUND(AVG(
        CASE
            WHEN LOWER(TRIM(timely_response)) = 'yes' THEN 100.0
            WHEN LOWER(TRIM(timely_response)) = 'no' THEN 0.0
            ELSE NULL
        END
    ), 2) AS timely_response_rate_pct
FROM complaints
WHERE date_received IS NOT NULL
GROUP BY DATE_FORMAT(date_received, '%Y-%m')
ORDER BY complaint_month;

-- 3. Complaint volume and response outcomes by financial product
-- Business Question: Which financial products generate the most complaints and how does timely-response performance vary by product?
-- What it does: Groups complaints by financial_product to report complaint count, percentage share of total volume, closed count, and timely-response rate.
-- Open complaints handling: Open complaints are included in complaint_count and share_of_complaints_pct, but excluded from timely_response_rate_pct because timely_response is NULL until the company responds.
SELECT
    COALESCE(financial_product, '(Missing)') AS financial_product,
    COUNT(*) AS complaint_count,
    ROUND(100.0 * COUNT(*) / NULLIF((SELECT COUNT(*) FROM complaints), 0), 2) AS share_of_complaints_pct,
    SUM(CASE WHEN LOWER(TRIM(response_status)) = 'closed' THEN 1 ELSE 0 END) AS closed_complaints,
    ROUND(AVG(
        CASE
            WHEN LOWER(TRIM(timely_response)) = 'yes' THEN 100.0
            WHEN LOWER(TRIM(timely_response)) = 'no' THEN 0.0
            ELSE NULL
        END
    ), 2) AS timely_response_rate_pct
FROM complaints
GROUP BY financial_product
ORDER BY complaint_count DESC;

-- 4. Most common issue categories
-- Business Question: Which issue categories drive the highest complaint volumes and span the most financial products?
-- What it does: Ranks the top 15 issue_category values by complaint count and counts distinct financial products affected per issue.
-- Open complaints handling: Open complaints are included because all filed complaints contribute to issue volume and product impact regardless of resolution status.
SELECT
    COALESCE(issue_category, '(Missing)') AS issue_category,
    COUNT(*) AS complaint_count,
    COUNT(DISTINCT financial_product) AS products_affected
FROM complaints
GROUP BY issue_category
ORDER BY complaint_count DESC
LIMIT 15;

-- 5. Top 10 companies by complaint volume and response performance
-- Business Question: Which 10 companies receive the most complaints and what are their closed counts and timely-response rates?
-- What it does: Aggregates complaint count, closed count, and timely-response percentage by company_name and returns the top 10 by volume.
-- Open complaints handling: Open complaints are included in complaint_count, but excluded from timely_response_rate_pct because Open rows have NULL timely_response (and AVG() ignores NULLs).
SELECT
    company_name,
    COUNT(*) AS complaint_count,
    SUM(CASE WHEN LOWER(TRIM(response_status)) = 'closed' THEN 1 ELSE 0 END) AS closed_complaints,
    ROUND(AVG(
        CASE
            WHEN LOWER(TRIM(timely_response)) = 'yes' THEN 100.0
            WHEN LOWER(TRIM(timely_response)) = 'no' THEN 0.0
            ELSE NULL
        END
    ), 2) AS timely_response_rate_pct
FROM complaints
GROUP BY company_name
ORDER BY complaint_count DESC
LIMIT 10;

-- 6. Complaint distribution by state
-- Business Question: How are complaints and reported companies distributed geographically across states?
-- What it does: Groups complaints by state (using 'Unknown' where missing states were filled during cleaning) to count complaints and distinct companies per state.
-- Open complaints handling: Open complaints are included because geographic distribution reflects all submitted complaints regardless of response status.
SELECT
    COALESCE(state, '(Missing)') AS state,
    COUNT(*) AS complaint_count,
    COUNT(DISTINCT company_name) AS companies_reported
FROM complaints
GROUP BY state
ORDER BY complaint_count DESC, state;

-- 7. Complaint volume and response performance by submission channel
-- Business Question: Which submission channels bring in the most complaints, and how do timely-response rates and open backlogs differ by channel?
-- What it does: Groups complaints by submission_channel to compute total complaint count, timely-response percentage, and open complaint count.
-- Open complaints handling: Open complaints are counted in complaint_count and open_complaints, but excluded from timely_response_rate_pct because timely_response is NULL for Open complaints.
SELECT
    COALESCE(submission_channel, '(Missing)') AS submission_channel,
    COUNT(*) AS complaint_count,
    ROUND(AVG(
        CASE
            WHEN LOWER(TRIM(timely_response)) = 'yes' THEN 100.0
            WHEN LOWER(TRIM(timely_response)) = 'no' THEN 0.0
            ELSE NULL
        END
    ), 2) AS timely_response_rate_pct,
    SUM(CASE WHEN LOWER(TRIM(response_status)) = 'open' THEN 1 ELSE 0 END) AS open_complaints
FROM complaints
GROUP BY submission_channel
ORDER BY complaint_count DESC;

-- 8. Complaint counts by response status and company response
-- Business Question: What is the breakdown of complaint outcomes across response_status and company_response?
-- What it does: Groups by response_status and company_response to count complaints in each status-outcome combination.
-- Open complaints handling: Open complaints are included (e.g., Open / In progress) so pending volume is visible alongside closed resolution categories.
SELECT
    COALESCE(response_status, '(Missing)') AS response_status,
    COALESCE(company_response, '(Missing)') AS company_response,
    COUNT(*) AS complaint_count
FROM complaints
GROUP BY response_status, company_response
ORDER BY complaint_count DESC, response_status, company_response;

-- 9. Response turnaround time by financial product
-- Business Question: What are the average, minimum, and maximum response turnaround times (in days) for each financial product?
-- What it does: Computes AVG, MIN, and MAX of DATEDIFF(date_company_responded, date_received) grouped by financial_product.
-- Open complaints handling: Open complaints are excluded via date_company_responded IS NOT NULL because they have not yet received a response date, so turnaround time cannot be measured.
SELECT
    COALESCE(financial_product, '(Missing)') AS financial_product,
    COUNT(*) AS complaints_with_response_dates,
    ROUND(AVG(DATEDIFF(date_company_responded, date_received)), 2) AS avg_days_to_respond,
    MIN(DATEDIFF(date_company_responded, date_received)) AS min_days_to_respond,
    MAX(DATEDIFF(date_company_responded, date_received)) AS max_days_to_respond
FROM complaints
WHERE date_received IS NOT NULL
  AND date_company_responded IS NOT NULL
GROUP BY financial_product
ORDER BY avg_days_to_respond DESC;

-- 10. Open complaints past their response due date
-- Business Question: Which open complaints are past their response due date as of 2026-11-25, and how many days overdue are they?
-- What it does: Lists unresolved Open complaints whose response_due_date is before 2026-11-25 and calculates days_past_due using '2026-11-25', ordered from most overdue.
-- Open complaints handling: Closed complaints are excluded and only Open complaints with NULL date_company_responded are selected to isolate the active overdue backlog.
SELECT
    complaint_id,
    company_name,
    financial_product,
    issue_category,
    state,
    date_received,
    response_due_date,
    DATEDIFF('2026-11-25', response_due_date) AS days_past_due
FROM complaints
WHERE LOWER(TRIM(response_status)) = 'open'
  AND date_company_responded IS NULL
  AND response_due_date < '2026-11-25'
ORDER BY days_past_due DESC, response_due_date;
