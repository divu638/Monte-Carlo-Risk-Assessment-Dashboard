"""
Financial Statement CSV/Excel Parser — RiskGuard Pro

Parses uploaded corporate financial statements in CSV format,
maps flexible column/row names to standard financial parameters,
and validates quantitative inputs for downstream ratio computation.
"""

import io
import csv
from typing import Dict, Any, Tuple


# Flexible mapping for header aliases
FIELD_ALIASES = {
    "current_assets": ["current assets", "current_assets", "ca", "currentassets"],
    "current_liabilities": ["current liabilities", "current_liabilities", "cl", "currentliabilities"],
    "cash_and_equivalents": ["cash", "cash and equivalents", "cash & cash equivalents", "cash_and_equivalents"],
    "inventory": ["inventory", "inventories", "stock", "stock in trade"],
    "total_assets": ["total assets", "total_assets", "assets"],
    "total_debt": ["total debt", "total_debt", "debt", "borrowings", "short and long term debt"],
    "total_equity": ["total equity", "equity", "shareholder equity", "net worth", "owners equity"],
    "revenue": ["revenue", "sales", "turnover", "total revenue", "gross sales"],
    "gross_profit": ["gross profit", "gross_profit", "gross margin amount"],
    "net_profit": ["net profit", "net income", "profit after tax", "pat", "net_profit"],
    "ebit": ["ebit", "operating profit", "operating income"],
    "ebitda": ["ebitda", "operating profit before depreciation"],
    "interest_expense": ["interest", "interest expense", "finance costs"],
    "accounts_receivable": ["accounts receivable", "receivables", "debtors", "trade receivables"],
    "retained_earnings": ["retained earnings", "reserves and surplus"]
}


def parse_financial_csv(content_str: str) -> Tuple[Dict[str, float], list]:
    """
    Parse CSV content supporting both Key-Value rows and Columnar Header rows.
    Returns (parsed_data_dict, list_of_warnings).
    """
    warnings = []
    data = {}
    
    # Normalize line endings
    content_str = content_str.replace('\r\n', '\n').replace('\r', '\n')
    reader = csv.reader(io.StringIO(content_str))
    rows = [row for row in reader if row and any(cell.strip() for cell in row)]
    
    if not rows:
        return data, ["The uploaded CSV file is empty."]

    # Check format:
    # Format A: Key-Value pairs (e.g. Column 1 = Metric Name, Column 2 = Value)
    # Format B: Tabular Header with single data row
    is_key_value = len(rows) > 3 and len(rows[0]) <= 3

    if is_key_value:
        for row in rows:
            if len(row) < 2:
                continue
            raw_key = row[0].strip().lower()
            raw_val = row[1].strip().replace(',', '').replace('₹', '').replace('$', '')
            
            # Match against aliases
            matched_field = None
            for field, aliases in FIELD_ALIASES.items():
                if raw_key == field or raw_key in aliases or any(a in raw_key for a in aliases):
                    matched_field = field
                    break
            
            if matched_field:
                try:
                    val = float(raw_val)
                    data[matched_field] = val
                except ValueError:
                    warnings.append(f"Could not parse numeric value for '{row[0]}': {raw_val}")
    else:
        # Tabular format (Row 0 = headers, Row 1 = values)
        headers = [h.strip().lower() for h in rows[0]]
        val_row = rows[1] if len(rows) > 1 else []
        for i, h in enumerate(headers):
            if i >= len(val_row):
                break
            raw_val = val_row[i].strip().replace(',', '').replace('₹', '').replace('$', '')
            for field, aliases in FIELD_ALIASES.items():
                if h == field or h in aliases:
                    try:
                        data[field] = float(raw_val)
                    except ValueError:
                        warnings.append(f"Could not parse numeric value for '{h}': {raw_val}")
                    break

    # Impute logical dependencies if not explicitly provided
    if "gross_profit" not in data and "revenue" in data:
        data["gross_profit"] = round(data["revenue"] * 0.35, 2)
    if "ebit" not in data and "net_profit" in data:
        data["ebit"] = round(data["net_profit"] * 1.35, 2)
    if "total_assets" not in data and "current_assets" in data:
        data["total_assets"] = round(data["current_assets"] * 1.8, 2)

    return data, warnings


def generate_sample_csv() -> str:
    """Generate sample CSV template formatted as Metric, Value."""
    sample_rows = [
        ["Financial Metric", "Value (₹ Lakhs)"],
        ["Revenue / Annual Turnover", "2400.00"],
        ["Cost of Goods Sold (COGS)", "1680.00"],
        ["Gross Profit", "720.00"],
        ["Operating Profit (EBIT)", "360.00"],
        ["Net Profit / PAT", "240.00"],
        ["Interest Expense", "45.00"],
        ["Current Assets", "650.00"],
        ["Cash & Equivalents", "120.00"],
        ["Inventory", "210.00"],
        ["Accounts Receivable", "180.00"],
        ["Current Liabilities", "420.00"],
        ["Total Debt / Borrowings", "550.00"],
        ["Total Equity / Net Worth", "850.00"],
        ["Total Assets", "1820.00"],
        ["Retained Earnings", "350.00"]
    ]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(sample_rows)
    return output.getvalue()
