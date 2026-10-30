"""
Unit tests for Financial Statement Parser (statement_parser.py)
Validates parsing of Key-Value CSV, Columnar CSV, JSON, Currency symbols (₹, $, €),
scale notation (Crore, Lakh), and accurate derivation of accounting identities.
"""

import pytest
from server.services.statement_parser import parse_financial_csv, _clean_numeric_value, FIELD_ALIASES


def test_clean_numeric_value():
    assert _clean_numeric_value("₹1,25,00,000") == 12500000.0
    assert _clean_numeric_value("$4,500.50") == 4500.50
    assert _clean_numeric_value("(50,000)") == -50000.0
    assert _clean_numeric_value("-1200") == -1200.0
    assert _clean_numeric_value("12.5 Cr") == 125000000.0
    assert _clean_numeric_value("85 Lakh") == 8500000.0
    assert _clean_numeric_value("150k") == 150000.0
    assert _clean_numeric_value("2.5M") == 2500000.0


def test_parse_key_value_csv():
    csv_text = """
    Line Item, Amount
    Revenue from Operations, ₹10,00,00,000
    Cost of Goods Sold (COGS), ₹6,00,00,000
    Operating Profit (EBIT), ₹1,80,00,000
    Net Profit, ₹1,20,00,000
    Interest Expense, ₹30,00,000
    Current Assets, ₹4,00,00,000
    Inventory, ₹1,50,00,000
    Current Liabilities, ₹2,00,00,000
    Total Debt, ₹2,50,00,000
    Shareholders' Equity, ₹3,50,00,000
    """
    data, warnings = parse_financial_csv(csv_text)
    assert not warnings
    assert data["revenue"] == 100000000.0
    assert data["cogs"] == 60000000.0
    assert data["gross_profit"] == 40000000.0  # Derived: 10 Cr - 6 Cr
    assert data["ebit"] == 18000000.0
    assert data["net_profit"] == 12000000.0
    assert data["current_assets"] == 40000000.0
    assert data["inventory"] == 15000000.0
    assert data["current_liabilities"] == 20000000.0
    assert data["total_debt"] == 25000000.0
    assert data["total_equity"] == 35000000.0


def test_parse_json_statement():
    json_text = """{
        "revenue": 5000000,
        "cogs": 3000000,
        "operating_expenses": 800000,
        "current_assets": 2000000,
        "inventory": 600000,
        "current_liabilities": 1000000,
        "total_debt": 1500000,
        "total_equity": 2500000
    }"""
    data, warnings = parse_financial_csv(json_text)
    assert not warnings
    assert data["revenue"] == 5000000.0
    assert data["cogs"] == 3000000.0
    assert data["gross_profit"] == 2000000.0
    assert data["ebit"] == 1200000.0  # 2000000 - 800000

