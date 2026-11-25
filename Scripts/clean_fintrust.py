"""Assess and clean the FinTrust 360 complaint dataset.

Reads Dataset/lecture-file.csv without changing it and writes the cleaned
outputs to Dataset/FinTrust_Cleaned.xlsx and Dataset/FinTrust_Cleaned.csv.
"""

from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


PROJECT_DIR = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_DIR / "Dataset" / "lecture-file.csv"
OUTPUT = PROJECT_DIR / "Dataset" / "FinTrust_Cleaned.xlsx"
CSV_OUTPUT = PROJECT_DIR / "Dataset" / "FinTrust_Cleaned.csv"
DATE_COLUMNS = ["date_received", "response_due_date", "date_company_responded"]
CATEGORY_COLUMNS = ["financial_product", "submission_channel"]
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def standardize_category(series: pd.Series) -> tuple[pd.Series, dict[str, dict[str, int]]]:
    """Trim and case-fold known labels to an existing canonical spelling."""
    present = series.dropna().astype(str)
    trimmed_counts = present.map(str.strip).value_counts()
    canonical_by_key: dict[str, str] = {}
    for value in trimmed_counts.index:
        key = value.casefold()
        if key not in canonical_by_key or trimmed_counts[value] > trimmed_counts[canonical_by_key[key]]:
            canonical_by_key[key] = value

    changes: dict[str, dict[str, int]] = {}
    result = series.copy()
    for old in present.unique():
        new = canonical_by_key[old.strip().casefold()]
        if old != new:
            changes.setdefault(new, {})[old] = int((series == old).sum())
            result = result.mask(series == old, new)
    return result, changes


def add_table_sheet(writer: pd.ExcelWriter, name: str, frame: pd.DataFrame) -> None:
    frame.to_excel(writer, sheet_name=name, index=False)
    ws = writer.book[name]
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    ws.row_dimensions[1].height = 25
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="17365D")
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    for column_cells in ws.columns:
        column_index = column_cells[0].column
        header = str(column_cells[0].value or "")
        max_value = max((len(str(cell.value)) for cell in column_cells[1:] if cell.value is not None), default=0)
        ws.column_dimensions[get_column_letter(column_index)].width = min(max(max(len(header) + 2, max_value + 2), 12), 52)
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=False)
    for col_name in DATE_COLUMNS:
        if col_name in frame.columns:
            col_index = frame.columns.get_loc(col_name) + 1
            for row_index in range(2, len(frame) + 2):
                ws.cell(row=row_index, column=col_index).number_format = "DD-MM-YYYY"


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Source CSV not found: {SOURCE}")

    raw = pd.read_csv(SOURCE, dtype="string")
    required = {"complaint_id", *DATE_COLUMNS, *CATEGORY_COLUMNS, "response_status", "timely_response"}
    missing_columns = required.difference(raw.columns)
    if missing_columns:
        raise ValueError(f"Source is missing required columns: {sorted(missing_columns)}")

    original_count = len(raw)
    source_whitespace_counts = {
        column: int(raw[column].dropna().map(lambda value: value != value.strip()).sum())
        for column in raw.columns
        if pd.api.types.is_string_dtype(raw[column].dtype)
    }
    # Check ID duplication and full-row equality before removing any records.
    repeated_id_mask = raw["complaint_id"].duplicated(keep=False)
    exact_duplicate_mask = raw.duplicated(keep="first")
    duplicate_records = raw.loc[exact_duplicate_mask].copy()
    duplicate_records.insert(0, "source_row_number", duplicate_records.index + 2)
    duplicate_records["removal_reason"] = "Exact duplicate full record; first copy retained"

    # Keep the first full-record copy. Any repeated IDs with differing contents
    # remain in the data and are described in the quality summary.
    cleaned = raw.loc[~exact_duplicate_mask].copy().reset_index(drop=True)

    category_changes: dict[str, dict[str, dict[str, int]]] = {}
    for column in CATEGORY_COLUMNS:
        cleaned[column], changes = standardize_category(cleaned[column])
        category_changes[column] = changes

    date_audit: list[dict[str, object]] = []
    parsed_dates: dict[str, pd.Series] = {}
    for column in DATE_COLUMNS:
        source_values = cleaned[column].copy()
        present = source_values.notna()
        iso_mask = source_values.fillna("").str.fullmatch(DATE_PATTERN)
        parsed = pd.to_datetime(source_values, format="mixed", errors="coerce")
        valid = present & parsed.notna()
        parsed_dates[column] = parsed
        date_audit.append({
            "column": column,
            "non_missing_values": int(present.sum()),
            "valid_dates_converted": int(valid.sum()),
            "unparseable_values_preserved_as_text": int((present & parsed.isna()).sum()),
            "ISO_YYYY_MM_DD_values": int((present & iso_mask).sum()),
            "format_consistent": bool((~present | iso_mask).all()),
        })
        # Store valid dates as Excel date values. Keep any invalid nonblank input
        # as-is rather than inventing or discarding information.
        cleaned[column] = parsed.where(valid, source_values)

    # Fill missing state with "Unknown" and track affected rows in state_missing_flag.
    missing_state_mask = cleaned["state"].isna() | (cleaned["state"].str.strip() == "")
    missing_state_count = int(missing_state_mask.sum())
    cleaned["state_missing_flag"] = missing_state_mask
    cleaned["state"] = cleaned["state"].mask(missing_state_mask, "Unknown")

    # Add response_days (date_company_responded minus date_received); keep blank for Open.
    is_open = cleaned["response_status"].str.casefold() == "open"
    valid_response_pair = (
        ~is_open
        & parsed_dates["date_company_responded"].notna()
        & parsed_dates["date_received"].notna()
    )
    cleaned["response_days"] = pd.Series(pd.NA, index=cleaned.index, dtype="Int64")
    cleaned.loc[valid_response_pair, "response_days"] = (
        parsed_dates["date_company_responded"].loc[valid_response_pair]
        - parsed_dates["date_received"].loc[valid_response_pair]
    ).dt.days.astype("Int64")

    # The source has Open rows with missing date_company_responded and
    # timely_response; leave those blanks as they are.
    missing_frame = pd.DataFrame({
        "column": cleaned.columns,
        "missing_count": [int(cleaned[c].isna().sum()) for c in cleaned.columns],
        "missing_percent": [round(float(cleaned[c].isna().mean() * 100), 2) for c in cleaned.columns],
    })

    # Identify repeated IDs that were not exact duplicate rows and retain them.
    repeated_id_counts = raw.loc[repeated_id_mask, "complaint_id"].value_counts()
    nonidentical_repeated_ids = []
    for complaint_id in repeated_id_counts.index:
        group = raw.loc[raw["complaint_id"] == complaint_id]
        if len(group.drop_duplicates()) > 1:
            nonidentical_repeated_ids.append(str(complaint_id))

    open_missing_response_date = int((is_open & cleaned["date_company_responded"].isna()).sum())
    open_missing_timely = int((is_open & cleaned["timely_response"].isna()).sum())
    open_count = int(is_open.sum())

    summary_rows: list[dict[str, str | int | float]] = [
        {"section": "Row and duplicate checks", "metric": "Original row count", "value": original_count, "details": "Source CSV rows"},
        {"section": "Row and duplicate checks", "metric": "Final row count", "value": len(cleaned), "details": "After removing exact full-record duplicates"},
        {"section": "Row and duplicate checks", "metric": "Duplicate records removed", "value": len(duplicate_records), "details": "Exact full-record duplicate copies; first copy retained"},
        {"section": "Row and duplicate checks", "metric": "Rows involved in repeated complaint IDs", "value": int(repeated_id_mask.sum()), "details": f"{raw.loc[repeated_id_mask, 'complaint_id'].nunique()} repeated IDs were checked before removal"},
        {"section": "Row and duplicate checks", "metric": "Repeated IDs with differing records", "value": len(nonidentical_repeated_ids), "details": ", ".join(nonidentical_repeated_ids) if nonidentical_repeated_ids else "None; no nonidentical repeated-ID records"},
        {"section": "Date checks", "metric": "Date interpretation", "value": "YYYY-MM-DD", "details": "Source dates checked against ISO format; valid dates converted to Excel date values and displayed DD-MM-YYYY"},
        {"section": "Missing-value rules", "metric": "Open complaints with missing response date", "value": open_missing_response_date, "details": "Preserved as missing; response_days kept blank"},
        {"section": "Missing-value rules", "metric": "Open complaints with missing timely response", "value": open_missing_timely, "details": "Preserved as missing"},
        {"section": "Missing-value rules", "metric": "Rows with missing state", "value": missing_state_count, "details": "Filled with 'Unknown' and flagged in state_missing_flag; no rows removed"},
    ]
    for audit in date_audit:
        summary_rows.append({
            "section": "Date checks",
            "metric": f"{audit['column']} format / conversion",
            "value": f"{audit['valid_dates_converted']} valid; {audit['unparseable_values_preserved_as_text']} unparseable",
            "details": f"{audit['ISO_YYYY_MM_DD_values']} source values match YYYY-MM-DD; consistent={audit['format_consistent']}",
        })

    for column, count in source_whitespace_counts.items():
        if count:
            summary_rows.append({"section": "Whitespace checks", "metric": f"{column}: leading/trailing whitespace", "value": count, "details": "Source values before cleaning; category labels were normalized only where equivalent"})

    for column, groups in category_changes.items():
        if not groups:
            summary_rows.append({"section": "Category standardization", "metric": column, "value": "No variants found", "details": "No changes"})
        for canonical, variants in groups.items():
            for original, count in variants.items():
                summary_rows.append({"section": "Category standardization", "metric": column, "value": f"{original!r} → {canonical!r}", "details": f"{count} rows standardized; same label after trimming and case-folding"})
    summary = pd.DataFrame(summary_rows, columns=["section", "metric", "value", "details"])

    category_analysis = cleaned.groupby("issue_category", dropna=False).size().rename("complaint_count").reset_index().sort_values("complaint_count", ascending=False)
    product_analysis = cleaned.groupby("financial_product", dropna=False).size().rename("complaint_count").reset_index().sort_values("complaint_count", ascending=False)
    response_parts = []
    for column in ["response_status", "company_response", "timely_response"]:
        part = cleaned[column].fillna("(Missing)").value_counts(dropna=False).rename_axis("category").reset_index(name="complaint_count")
        part.insert(0, "dimension", column)
        response_parts.append(part)
    response_analysis = pd.concat(response_parts, ignore_index=True)

    fp_rows_fixed = sum(sum(variants.values()) for variants in category_changes.get("financial_product", {}).values())
    sc_rows_fixed = sum(sum(variants.values()) for variants in category_changes.get("submission_channel", {}).values())
    unparseable_dates = sum(int(audit["unparseable_values_preserved_as_text"]) for audit in date_audit)
    date_details = "; ".join(
        f"{audit['column']}: {audit['valid_dates_converted']} valid, {audit['unparseable_values_preserved_as_text']} unparseable"
        for audit in date_audit
    )

    cleaning_log = pd.DataFrame([
        {
            "step": "1. Duplicate removal",
            "issue found": "Exact full-record duplicate rows in source CSV",
            "rows affected": len(duplicate_records),
            "action taken": "Removed exact duplicate copies while retaining the first record; archived removed rows in Duplicate_Records",
            "rationale": "Prevents double-counting complaint volumes and KPI metrics while preserving all unique records",
        },
        {
            "step": "2. Category standardization (financial_product)",
            "issue found": "Leading/trailing whitespace and inconsistent letter casing in financial_product",
            "rows affected": fp_rows_fixed,
            "action taken": "Trimmed whitespace and normalized variants via case-folding to canonical product labels",
            "rationale": "Consolidates equivalent product labels so product aggregations and filters are accurate",
        },
        {
            "step": "3. Category standardization (submission_channel)",
            "issue found": "Leading/trailing whitespace and inconsistent letter casing in submission_channel",
            "rows affected": sc_rows_fixed,
            "action taken": "Trimmed whitespace and normalized variants via case-folding to canonical channel labels",
            "rationale": "Consolidates equivalent submission channels so channel performance comparisons are consistent",
        },
        {
            "step": "4. Missing state handling",
            "issue found": "Missing/blank values in state column",
            "rows affected": missing_state_count,
            "action taken": "Filled missing state values with 'Unknown' and added boolean state_missing_flag column",
            "rationale": "Keeps all complaint records in total counts while explicitly flagging incomplete state metadata",
        },
        {
            "step": "5. Date validation and turnaround",
            "issue found": f"Date columns stored as text strings requiring ISO YYYY-MM-DD validation ({unparseable_dates} unparseable values)",
            "rows affected": len(cleaned),
            "action taken": f"Validated and parsed dates ({date_details}); formatted as DD-MM-YYYY in Excel; added response_days (responded minus received)",
            "rationale": "Ensures reliable chronological sorting, date-range filtering, and turnaround calculation without altering invalid inputs",
        },
        {
            "step": "6. Open complaints blank fields",
            "issue found": f"Open complaints have blank date_company_responded ({open_missing_response_date}) and blank timely_response ({open_missing_timely})",
            "rows affected": open_count,
            "action taken": "Retained blank date_company_responded, timely_response, and response_days for Open complaints",
            "rationale": "Open complaints are still pending company resolution; preserving blanks avoids fabricating dates or timeliness outcomes",
        },
    ], columns=["step", "issue found", "rows affected", "action taken", "rationale"])

    duplicate_records = duplicate_records.reset_index(drop=True)
    cleaned.to_csv(CSV_OUTPUT, index=False)
    with pd.ExcelWriter(OUTPUT, engine="openpyxl", date_format="DD-MM-YYYY", datetime_format="DD-MM-YYYY") as writer:
        add_table_sheet(writer, "Cleaned_Data", cleaned)
        add_table_sheet(writer, "Cleaning_Log", cleaning_log)
        add_table_sheet(writer, "Missing_Values", missing_frame)
        add_table_sheet(writer, "Duplicate_Records", duplicate_records)
        add_table_sheet(writer, "Data_Quality_Summary", summary)
        add_table_sheet(writer, "Category_Analysis", category_analysis)
        add_table_sheet(writer, "Product_Analysis", product_analysis)
        add_table_sheet(writer, "Response_Analysis", response_analysis)

    status_counts = cleaned["response_status"].value_counts(dropna=False)
    print(f"Source: {SOURCE}")
    print(f"Output (XLSX): {OUTPUT}")
    print(f"Output (CSV): {CSV_OUTPUT}")
    print(f"Original rows: {original_count}")
    print(f"Final rows: {len(cleaned)}")
    print(f"Status breakdown - Closed: {int(status_counts.get('Closed', 0))}, Open: {int(status_counts.get('Open', 0))}")
    print(f"Exact duplicate records removed: {len(duplicate_records)}")
    print("Missing values by column:")
    print(missing_frame.to_string(index=False))
    print("Category standardizations:")
    for column, groups in category_changes.items():
        print(f"  {column}: {groups}")


if __name__ == "__main__":
    main()
