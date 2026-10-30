"""
Financial Statement CSV/Excel/Text Parser — RiskGuard Pro

Parses uploaded corporate financial statements in CSV/TSV/JSON format,
maps flexible column/row names to standard financial parameters,
and validates quantitative inputs for downstream ratio computation.
Supports both key-value exports and columnar formats, currency symbols (₹, $, €, £),
lakhs/crores notation, and accounting identities.
"""

import io
import csv
import re
import json
from typing import Dict, Any, Tuple


# Comprehensive mapping for financial field aliases across Indian & Global reporting standards
FIELD_ALIASES = {
    "revenue": [
        "revenue", "revenue from operations", "sales", "turnover", "total revenue",
        "gross sales", "net revenue", "net sales", "operating revenue", "topline",
        "income from operations"
    ],
    "cogs": [
        "cost of goods sold", "cogs", "cost of sales", "direct expenses", "cost of materials consumed",
        "production costs", "direct costs", "cost of revenue", "purchase of stock in trade"
    ],
    "gross_profit": [
        "gross profit", "gross_profit", "gp", "gross margin amount", "gross income"
    ],
    "ebit": [
        "ebit", "operating profit", "operating income", "pbit", "profit before interest and tax",
        "operating profit (ebit)", "earnings before interest and tax"
    ],
    "operating_expenses": [
        "operating expenses", "operating expense", "opex", "sga", "selling general and administrative",
        "administrative expenses", "employee benefits", "indirect expenses", "other expenses"
    ],
    "depreciation_amortization": [
        "depreciation", "depreciation and amortisation", "depreciation & amortisation", "depreciation and amortization",
        "amortisation", "amortization", "dna", "depreciation expense"
    ],
    "ebitda": [
        "ebitda", "operating profit before depreciation", "operating profit before dna",
        "earnings before interest taxes depreciation"
    ],
    "interest_expense": [
        "interest", "interest expense", "interest expenses", "finance costs", "borrowing costs",
        "finance charges", "interest paid"
    ],
    "profit_before_tax": [
        "profit before tax", "pbt", "ebt", "earnings before tax", "profit before taxation"
    ],
    "tax_expense": [
        "tax", "income tax", "taxes", "tax expense", "current tax", "provision for tax", "income tax expense"
    ],
    "net_profit": [
        "net profit", "net income", "profit after tax", "pat", "net_profit", "profit for the period",
        "bottom line", "net profit after tax", "profit after taxation"
    ],
    "current_assets": [
        "current assets", "current_assets", "ca", "currentassets", "total current assets"
    ],
    "cash_and_equivalents": [
        "cash", "cash and equivalents", "cash & cash equivalents", "cash & bank", "cash and bank",
        "cash and bank balances", "cash in hand", "bank balance", "cash equivalents"
    ],
    "short_term_investments": [
        "short term investments", "short-term investments", "marketable securities",
        "current investments", "st investments"
    ],
    "accounts_receivable": [
        "accounts receivable", "receivables", "debtors", "trade receivables", "sundry debtors",
        "bills receivable"
    ],
    "inventory": [
        "inventory", "inventories", "stock", "stock in trade", "finished goods",
        "raw materials", "work-in-progress", "work in progress", "wip", "closing stock", "closing inventory"
    ],
    "prepaid_expenses": [
        "prepaid expenses", "prepaid expense", "prepayments", "expenses paid in advance",
        "advance tax", "prepaid"
    ],
    "other_current_assets": [
        "other current assets", "short term advances", "recoverable taxes", "other ca"
    ],
    "current_liabilities": [
        "current liabilities", "current_liabilities", "cl", "currentliabilities",
        "total current liabilities"
    ],
    "accounts_payable": [
        "accounts payable", "trade payables", "payables", "creditors", "sundry creditors",
        "bills payable"
    ],
    "short_term_borrowings": [
        "short term borrowings", "short-term borrowings", "short term debt", "short term loans",
        "bank overdraft", "cash credit", "current borrowings", "st debt"
    ],
    "outstanding_expenses": [
        "outstanding expenses", "accrued expenses", "expenses payable", "accrued liabilities"
    ],
    "taxes_payable": [
        "taxes payable", "tax payable", "provision for taxation", "income tax payable"
    ],
    "current_portion_debt": [
        "current portion of long-term debt", "current maturities of long term debt", "current portion of debt"
    ],
    "total_debt": [
        "total debt", "total_debt", "debt", "borrowings", "short and long term debt",
        "total borrowings", "secured loans", "loan liabilities"
    ],
    "long_term_borrowings": [
        "long term borrowings", "long-term borrowings", "long term debt", "term loans",
        "non-current liabilities", "debentures", "bonds"
    ],
    "total_equity": [
        "total equity", "equity", "shareholder equity", "shareholders equity", "shareholders' equity",
        "net worth", "owners equity", "total net worth", "share capital"
    ],
    "share_capital": [
        "share capital", "equity share capital", "paid up capital", "capital"
    ],
    "retained_earnings": [
        "retained earnings", "reserves and surplus", "reserves & surplus", "accumulated profits",
        "general reserve", "reserves"
    ],
    "non_current_assets": [
        "non current assets", "non-current assets", "fixed assets", "net fixed assets",
        "property plant and equipment", "ppe", "gross block", "net block", "capital work in progress"
    ],
    "total_assets": [
        "total assets", "total_assets", "assets", "balance sheet total"
    ],
    "total_liabilities": [
        "total liabilities", "total_liabilities", "liabilities"
    ],
    "credit_sales": [
        "credit sales", "net credit sales", "annual credit sales"
    ],
    "credit_purchases": [
        "credit purchases", "net credit purchases", "purchases", "annual credit purchases"
    ],
    "avg_inventory": [
        "average inventory", "avg inventory", "avg_inventory"
    ],
    "avg_receivables": [
        "average receivables", "avg receivables", "avg_receivables", "average trade receivables"
    ],
    "avg_payables": [
        "average payables", "avg payables", "avg_payables", "average trade payables"
    ],
    "operating_cash_flow": [
        "operating cash flow", "cash flow from operations", "cash flow available for debt service", "cfads"
    ],
    "total_debt_service": [
        "total debt service", "debt service", "debt servicing", "principal and interest", "total debt repayments"
    ]
}


def _clean_numeric_value(val_str: str) -> float:
    """Parse number supporting commas, currencies (₹, $, €, £), parentheses for negative, and scale suffixes."""
    if not val_str:
        raise ValueError("Empty string")
    
    val_str = str(val_str).strip()
    # Check for negative in parentheses e.g. (50,000)
    is_neg = False
    if val_str.startswith('(') and val_str.endswith(')'):
        is_neg = True
        val_str = val_str[1:-1].strip()
    elif val_str.startswith('-'):
        is_neg = True
        val_str = val_str[1:].strip()

    # Strip currency signs & common whitespace
    for char in ['₹', '$', '€', '£', ',', ' ']:
        val_str = val_str.replace(char, '')

    # Check for multiplier units like Cr, Lakh, k, M
    multiplier = 1.0
    val_lower = val_str.lower()
    if 'cr' in val_lower or 'crore' in val_lower:
        multiplier = 10_000_000.0
        val_str = re.sub(r'(cr|crores?|crore)', '', val_str, flags=re.I).strip()
    elif 'lakh' in val_lower or 'lac' in val_lower or val_lower.endswith('l'):
        multiplier = 100_000.0
        val_str = re.sub(r'(lakhs?|lacs?|lac|l)', '', val_str, flags=re.I).strip()
    elif 'm' in val_lower or 'million' in val_lower:
        multiplier = 1_000_000.0
        val_str = re.sub(r'(millions?|million|m)', '', val_str, flags=re.I).strip()
    elif 'k' in val_lower:
        multiplier = 1_000.0
        val_str = re.sub(r'(k)', '', val_str, flags=re.I).strip()

    num = float(val_str) * multiplier
    return -num if is_neg else num


def _match_field(key_str: str) -> str:
    """Match a cleaned raw key against known FIELD_ALIASES using exact & word-boundary matching."""
    if not key_str:
        return None
    clean = str(key_str).lower().strip()
    clean = re.sub(r'[\(\[\{].*?[\)\]\}]', '', clean)  # remove parenthesized hints like (₹) or (INR)
    clean = re.sub(r'[^a-z0-9\s&_]', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()

    if not clean:
        return None

    # 1. Exact match first
    for field, aliases in FIELD_ALIASES.items():
        if clean == field or clean in aliases:
            return field

    # 2. Whole-word / phrase match, sorting aliases by descending length so specific terms take priority
    all_candidates = []
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            all_candidates.append((len(alias), field, alias))
    all_candidates.sort(reverse=True, key=lambda x: x[0])

    for _, field, alias in all_candidates:
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, clean):
            return field

    return None


def parse_financial_csv(content_str: str) -> Tuple[Dict[str, float], list]:
    """
    Parse CSV / TSV / JSON content supporting both Key-Value rows and Columnar Header rows.
    Returns (parsed_data_dict, list_of_warnings).
    """
    warnings = []
    data = {}
    
    if not content_str or not content_str.strip():
        return data, ["The uploaded statement content is empty."]

    # Try JSON format first
    content_str_trimmed = content_str.strip()
    if content_str_trimmed.startswith('{') and content_str_trimmed.endswith('}'):
        try:
            parsed_json = json.loads(content_str_trimmed)
            for k, v in parsed_json.items():
                matched = _match_field(str(k))
                if matched:
                    try:
                        data[matched] = _clean_numeric_value(str(v))
                    except ValueError:
                        warnings.append(f"Could not parse numeric value for '{k}': {v}")
            if data:
                _derive_accounting_identities(data)
                return data, warnings
        except Exception:
            pass  # Fallback to CSV reader

    # Normalize line endings
    content_str = content_str.replace('\r\n', '\n').replace('\r', '\n')
    
    # Detect delimiter: comma, tab, or semicolon
    sample = content_str[:2048]
    delimiter = ','
    if '\t' in sample and sample.count('\t') > sample.count(','):
        delimiter = '\t'
    elif ';' in sample and sample.count(';') > sample.count(','):
        delimiter = ';'

    reader = csv.reader(io.StringIO(content_str), delimiter=delimiter)
    rows = [[c.strip() for c in row] for row in reader if row and any(cell.strip() for cell in row)]
    
    if not rows:
        return data, ["The uploaded CSV file is empty or could not be parsed."]

    # Detect format:
    # Key-Value format: Column 0 is metric name, Column 1 (or last col) is value
    # Columnar format: Row 0 is headers, subsequent row is values
    is_key_value = len(rows) >= 2 and len(rows[0]) <= 4 and any(
        _match_field(r[0]) is not None for r in rows[:min(5, len(rows))]
    )

    if is_key_value:
        for row in rows:
            if len(row) < 2:
                continue
            raw_key = row[0]
            matched_field = _match_field(raw_key)
            if not matched_field:
                continue
                
            val_found = False
            # 1. Try joined remainder first (handles unquoted comma numbers like ₹10,00,00,000)
            joined_remainder = "".join(row[1:]).strip()
            try:
                data[matched_field] = _clean_numeric_value(joined_remainder)
                val_found = True
            except ValueError:
                # 2. Try individual cells
                for cell in row[1:]:
                    if not cell:
                        continue
                    try:
                        data[matched_field] = _clean_numeric_value(cell)
                        val_found = True
                        break
                    except ValueError:
                        continue
            if not val_found and row[1]:
                warnings.append(f"Could not parse numeric value for '{raw_key}': {row[1]}")
    else:
        # Tabular format: Headers in row 0
        headers = [_match_field(h) for h in rows[0]]
        val_row = rows[1] if len(rows) > 1 else []
        for i, matched_field in enumerate(headers):
            if not matched_field or i >= len(val_row):
                continue
            try:
                data[matched_field] = _clean_numeric_value(val_row[i])
            except ValueError:
                warnings.append(f"Could not parse numeric value for '{rows[0][i]}': {val_row[i]}")

    # Derive missing components strictly from standard accounting identities
    _derive_accounting_identities(data)

    return data, warnings


def _derive_accounting_identities(data: Dict[str, float]):
    """Derive missing financial items using exact accounting formulas."""
    # 1. Gross Profit = Revenue - COGS
    if "gross_profit" not in data and "revenue" in data and "cogs" in data:
        data["gross_profit"] = round(data["revenue"] - data["cogs"], 2)
    elif "cogs" not in data and "revenue" in data and "gross_profit" in data:
        data["cogs"] = round(data["revenue"] - data["gross_profit"], 2)

    # 2. EBIT = Gross Profit - Operating Expenses (or Revenue - COGS - Operating Expenses)
    if "ebit" not in data:
        if "gross_profit" in data and "operating_expenses" in data:
            data["ebit"] = round(data["gross_profit"] - data["operating_expenses"], 2)
        elif "revenue" in data and "cogs" in data and "operating_expenses" in data:
            data["ebit"] = round(data["revenue"] - data["cogs"] - data["operating_expenses"], 2)
        elif "net_profit" in data and "interest_expense" in data:
            tax = data.get("tax_expense", 0.0)
            data["ebit"] = round(data["net_profit"] + data["interest_expense"] + tax, 2)

    # 3. EBITDA = EBIT + Depreciation & Amortisation
    if "ebitda" not in data and "ebit" in data:
        dna = data.get("depreciation_amortization", 0.0)
        data["ebitda"] = round(data["ebit"] + dna, 2)

    # 4. Net Profit = Profit Before Tax - Tax Expense
    if "net_profit" not in data and "profit_before_tax" in data:
        tax = data.get("tax_expense", 0.0)
        data["net_profit"] = round(data["profit_before_tax"] - tax, 2)

    # 5. Current Assets aggregation
    ca_components = ["cash_and_equivalents", "accounts_receivable", "inventory", "short_term_investments", "prepaid_expenses", "other_current_assets"]
    if "current_assets" not in data and any(k in data for k in ca_components):
        data["current_assets"] = sum(data.get(k, 0.0) for k in ca_components)

    # 6. Current Liabilities aggregation
    cl_components = ["accounts_payable", "short_term_borrowings", "outstanding_expenses", "taxes_payable", "current_portion_debt"]
    if "current_liabilities" not in data and any(k in data for k in cl_components):
        data["current_liabilities"] = sum(data.get(k, 0.0) for k in cl_components)

    # 7. Total Debt = Short-Term Borrowings + Long-Term Borrowings
    if "total_debt" not in data:
        if "short_term_borrowings" in data or "long_term_borrowings" in data:
            data["total_debt"] = round(data.get("short_term_borrowings", 0.0) + data.get("long_term_borrowings", 0.0), 2)

    # 8. Shareholders' Equity = Share Capital + Reserves and Surplus
    if "total_equity" not in data:
        if "share_capital" in data or "retained_earnings" in data:
            data["total_equity"] = round(data.get("share_capital", 0.0) + data.get("retained_earnings", 0.0), 2)

    # 9. Total Assets = Current Assets + Non-Current Assets
    if "total_assets" not in data and "current_assets" in data and "non_current_assets" in data:
        data["total_assets"] = round(data["current_assets"] + data["non_current_assets"], 2)
    elif "total_assets" not in data and "total_debt" in data and "total_equity" in data:
        # Balance sheet identity: Assets = Total Liabilities/Debt + Equity
        data["total_assets"] = round(data["total_debt"] + data["total_equity"], 2)

    # 10. Averages defaults
    if "avg_inventory" not in data and "inventory" in data:
        data["avg_inventory"] = data["inventory"]
    if "avg_receivables" not in data and "accounts_receivable" in data:
        data["avg_receivables"] = data["accounts_receivable"]
    if "avg_payables" not in data and "accounts_payable" in data:
        data["avg_payables"] = data["accounts_payable"]
    if "credit_sales" not in data and "revenue" in data:
        data["credit_sales"] = data["revenue"]


def _pick_best_figure(nums: list) -> str:
    """Select the current year financial figure from a list of numbers on a table row."""
    if not nums:
        return None
    if len(nums) == 1:
        return nums[0]

    first = nums[0].strip()
    # Check if first is a note number: e.g. integer 1 to 60 without decimal points or currency symbols
    clean_first = re.sub(r'[^\d]', '', first)
    if clean_first.isdigit() and 1 <= int(clean_first) <= 60 and '.' not in first and not any(c in first for c in ['₹', '$', '€', '£', 'cr', 'lakh', 'mn', 'k', 'Cr', 'Lakh']):
        # If second number exists, it is the Current Year amount!
        return nums[1]

    # Otherwise, first number is the current year amount
    return nums[0]


def parse_financial_pdf(file_bytes: bytes) -> Tuple[Dict[str, float], list]:
    """
    Parse uploaded corporate financial statements in PDF format.
    Scans pages, identifies Balance Sheet and P&L tables, extracts metric amounts,
    and applies standard accounting identities.
    Returns (data_dict, list_of_warnings).
    """
    warnings = []
    data = {}
    if not file_bytes:
        return data, ["The uploaded PDF file is empty."]

    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        num_pages = len(reader.pages)
        if num_pages == 0:
            return data, ["PDF contains no readable pages."]
    except Exception as e:
        return data, [f"Could not open PDF file: {str(e)}"]

    # Identify candidate financial statement pages
    statement_keywords = [
        "balance sheet", "statement of profit and loss", "profit & loss",
        "income statement", "statement of financial position", "statement of operations",
        "revenue from operations", "current assets", "current liabilities",
        "turnover", "total assets", "equity and liabilities"
    ]

    all_page_texts = []
    priority_pages = []

    for idx, page in enumerate(reader.pages):
        try:
            ptxt = page.extract_text() or ""
        except Exception:
            ptxt = ""
        all_page_texts.append(ptxt)
        plow = ptxt.lower()
        if any(kw in plow for kw in statement_keywords):
            priority_pages.append(idx)

    # Scan prioritized pages first; if none found, scan first 15 pages
    target_pages = priority_pages if priority_pages else list(range(min(15, num_pages)))

    # Check for unit scales: (₹ in Lakhs), (₹ in Crores), (in Millions), (in Thousands)
    global_multiplier = 1.0
    for idx in target_pages:
        txt = all_page_texts[idx].lower()
        if re.search(r'\(?\s*(?:rs\.?|inr|₹)?\s*in\s+(?:crores?|cr)\b', txt):
            global_multiplier = 10_000_000.0
            break
        elif re.search(r'\(?\s*(?:rs\.?|inr|₹)?\s*in\s+(?:lakhs?|lac|lacs)\b', txt):
            global_multiplier = 100_000.0
            break
        elif re.search(r'\(?\s*(?:rs\.?|inr|₹|\$)?\s*in\s+(?:millions?|mn)\b', txt):
            global_multiplier = 1_000_000.0
            break
        elif re.search(r'\(?\s*(?:rs\.?|inr|₹|\$)?\s*in\s+(?:thousands?)\b', txt):
            global_multiplier = 1_000.0
            break

    # Regex to capture financial amounts: with optional currency symbols, commas, decimals, scales, parentheses
    num_pattern = re.compile(
        r'\(?\s*[\u20b9\$€£]?\s*[-–—]?\s*\d+(?:,\d+)*(?:\.\d+)?\s*(?:cr|crores?|lakhs?|lacs?|lac|million|m|k)?\s*\)?',
        re.IGNORECASE
    )

    for idx in target_pages:
        ptxt = all_page_texts[idx]
        lines = ptxt.splitlines()
        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            matches = list(num_pattern.finditer(line))
            if not matches:
                continue

            # Candidate label is the string before the first matched number
            first_m = matches[0]
            candidate_label = line[:first_m.start()].strip(' :-=\t–—()[]')

            matched_field = _match_field(candidate_label)
            if not matched_field and ':' in line:
                parts = line.split(':', 1)
                matched_field = _match_field(parts[0])

            if not matched_field:
                continue

            # Pick figure from matches
            nums = [m.group(0).strip() for m in matches]
            fig_str = _pick_best_figure(nums)
            if not fig_str:
                continue

            try:
                val = _clean_numeric_value(fig_str)
                # If number didn't have its own scale suffix and a global multiplier exists
                if global_multiplier > 1.0 and abs(val) < 1_000_000 and not any(u in fig_str.lower() for u in ['cr', 'crore', 'lakh', 'lac', 'million', 'm', 'k']):
                    val = val * global_multiplier

                # Set field if not yet populated
                if matched_field not in data:
                    data[matched_field] = val
            except ValueError:
                continue

    # Derive missing accounting identities
    _derive_accounting_identities(data)

    if not data:
        warnings.append(
            "No recognizable financial statement lines (such as Revenue, Operating Profit, Current Assets, Liabilities, or Equity) were detected in this PDF document."
        )

    return data, warnings


def parse_financial_excel(file_bytes: bytes) -> Tuple[Dict[str, float], list]:
    """
    Parse uploaded corporate financial statements in Excel (.xlsx, .xls) format.
    Supports both key-value metric rows and tabular columnar layouts.
    Returns (data_dict, list_of_warnings).
    """
    warnings = []
    data = {}
    if not file_bytes:
        return data, ["The uploaded Excel file is empty."]

    try:
        import openpyxl
        wb = openpyxl.load_workbook(filename=io.BytesIO(file_bytes), data_only=True)
    except Exception as e:
        return data, [f"Could not open Excel file: {str(e)}"]

    for sheet in wb.worksheets:
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            continue

        # 1. Key-Value rows: Column 0 or 1 is metric name, subsequent column is amount
        for row in rows:
            if not row or not any(row):
                continue
            first_cell = str(row[0] or "").strip()
            row_remainder = row[1:]
            if not first_cell and len(row) > 1 and row[1]:
                first_cell = str(row[1]).strip()
                row_remainder = row[2:]

            matched_field = _match_field(first_cell)
            if matched_field and matched_field not in data:
                for cell in row_remainder:
                    if cell is None or cell == "":
                        continue
                    if isinstance(cell, (int, float)):
                        data[matched_field] = float(cell)
                        break
                    else:
                        try:
                            val = _clean_numeric_value(str(cell))
                            data[matched_field] = val
                            break
                        except ValueError:
                            continue

        # 2. Tabular format: check header row if fewer than 3 fields detected
        if len(data) < 3 and len(rows) >= 2:
            headers = [_match_field(str(c or "").strip()) for c in rows[0]]
            if any(headers):
                val_row = rows[1]
                for i, h in enumerate(headers):
                    if h and h not in data and i < len(val_row) and val_row[i] is not None:
                        val = val_row[i]
                        if isinstance(val, (int, float)):
                            data[h] = float(val)
                        else:
                            try:
                                data[h] = _clean_numeric_value(str(val))
                            except ValueError:
                                pass

    _derive_accounting_identities(data)

    if not data:
        warnings.append(
            "No recognizable financial statement lines (such as Revenue, Operating Profit, Current Assets, Liabilities, or Equity) were detected in this Excel sheet."
        )

    return data, warnings


def generate_sample_excel() -> bytes:
    """Generate sample Excel template formatted as Metric, Value according to RiskGuard standard."""
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Financial Statements"
    rows = [
        ["Financial Line Item", "Amount (₹ Lakhs)", "Reporting Category"],
        ["Revenue from Operations", 2400.00, "Profit & Loss (Topline)"],
        ["Cost of Goods Sold (COGS)", 1680.00, "Direct Expenses"],
        ["Gross Profit", 720.00, "Gross Margin"],
        ["Operating Profit (EBIT)", 360.00, "Core Operating Earnings"],
        ["Net Profit / PAT", 240.00, "Bottom Line Profit"],
        ["Interest Expense", 45.00, "Finance Costs"],
        ["Current Assets", 650.00, "Short-Term Assets"],
        ["Cash & Bank Balances", 120.00, "Cash Liquidity"],
        ["Inventory & Stock", 210.00, "Working Capital Stock"],
        ["Accounts Receivable (Debtors)", 180.00, "Receivables"],
        ["Prepaid Expenses", 15.00, "Current Advances"],
        ["Current Liabilities", 420.00, "Short-Term Payables & Debt"],
        ["Accounts Payable (Creditors)", 160.00, "Trade Payables"],
        ["Total Debt / Borrowings", 550.00, "Secured & Unsecured Loans"],
        ["Total Equity / Net Worth", 850.00, "Shareholders Capital + Reserves"],
        ["Total Assets", 1820.00, "Balance Sheet Total"]
    ]
    for r in rows:
        ws.append(r)
    bio = io.BytesIO()
    wb.save(bio)
    return bio.getvalue()


def generate_sample_csv() -> str:
    """Generate sample CSV template formatted as Metric, Value according to RiskGuard standard."""
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
        ["Prepaid Expenses", "15.00"],
        ["Current Liabilities", "420.00"],
        ["Accounts Payable", "160.00"],
        ["Total Debt / Borrowings", "550.00"],
        ["Total Equity / Net Worth", "850.00"],
        ["Total Assets", "1820.00"],
        ["Retained Earnings", "350.00"]
    ]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(sample_rows)
    return output.getvalue()
