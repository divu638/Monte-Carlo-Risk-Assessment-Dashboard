"""
Unit & Sanity Tests for Financial Ratios Engine & Altman Z-Score (RiskGuard Pro)
Validates mathematical soundness, edge-case resilience (zero divisions),
Altman Z-Score zone classification, and industry benchmark comparisons.
"""

import os
import sys
import pytest
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))
from services.financial_ratios import (
    calculate_financial_ratios,
    calculate_altman_z,
    INDUSTRY_BENCHMARKS,
    _safe_div
)


def test_safe_div():
    """Verify division by zero and invalid inputs return fallback safely."""
    assert _safe_div(10, 2) == 5.0
    assert _safe_div(10, 0) is None
    assert _safe_div(10, 0, fallback=0.0) == 0.0
    assert _safe_div("abc", 5) is None
    assert _safe_div(5, None) is None


def test_altman_z_safe_zone():
    """Healthy firm financials should yield Z > 2.99 (Safe Zone)."""
    # Working Cap: 200, Assets: 1000, Retained: 300, EBIT: 150, Mkt Cap: 1200, Liab: 400, Rev: 1000
    res = calculate_altman_z(
        working_capital=200,
        total_assets=1000,
        retained_earnings=300,
        ebit=150,
        market_cap=1200,
        total_liabilities=400,
        revenue=1000
    )
    # X1 = 0.2 -> 0.24
    # X2 = 0.3 -> 0.42
    # X3 = 0.15 -> 0.495
    # X4 = 1200/400 = 3.0 -> 1.8
    # X5 = 1.0 -> 0.999
    # Z = 0.24 + 0.42 + 0.495 + 1.8 + 0.999 = 3.954
    assert res["zone"] == "Safe Zone"
    assert res["score"] > 2.99
    assert res["color"] == "success"


def test_altman_z_grey_zone():
    """Moderate distress firm should yield 1.81 <= Z <= 2.99 (Grey Zone)."""
    res = calculate_altman_z(
        working_capital=100,
        total_assets=1000,
        retained_earnings=150,
        ebit=80,
        market_cap=600,
        total_liabilities=500,
        revenue=900
    )
    assert res["zone"] == "Grey Zone"
    assert 1.81 <= res["score"] <= 2.99
    assert res["color"] == "warning"


def test_altman_z_distress_zone():
    """Heavily distressed firm should yield Z < 1.81 (Distress Zone)."""
    res = calculate_altman_z(
        working_capital=-100,
        total_assets=1000,
        retained_earnings=-200,
        ebit=-50,
        market_cap=100,
        total_liabilities=900,
        revenue=300
    )
    assert res["zone"] == "Distress Zone"
    assert res["score"] < 1.81
    assert res["color"] == "danger"


def test_altman_z_zero_assets():
    """Zero total assets should not throw ZeroDivisionError."""
    res = calculate_altman_z(0, 0, 0, 0, 0, 0, 0)
    assert res["score"] is None
    assert res["zone"] == "Unknown"


def test_financial_ratios_standard_company():
    """Test full financial ratio calculation suite on standard corporate numbers."""
    data = {
        "current_assets": 500,
        "current_liabilities": 250,
        "cash_and_equivalents": 100,
        "inventory": 150,
        "total_assets": 2000,
        "total_debt": 800,
        "total_equity": 1200,
        "total_liabilities": 800,
        "revenue": 2400,
        "gross_profit": 720,
        "net_profit": 240,
        "ebit": 360,
        "ebitda": 450,
        "interest_expense": 60,
        "accounts_receivable": 200,
        "retained_earnings": 400,
        "market_cap": 1500
    }

    results = calculate_financial_ratios(data, industry="Manufacturing")

    # Liquidity
    assert results["liquidity"]["current_ratio"] == 2.0  # 500 / 250
    assert results["liquidity"]["quick_ratio"] == 1.4    # (500-150)/250
    assert results["liquidity"]["cash_ratio"] == 0.4     # 100/250
    assert results["liquidity"]["working_capital"] == 250

    # Leverage
    assert results["leverage"]["de_ratio"] == round(800 / 1200, 2)  # 0.67
    assert results["leverage"]["debt_ratio"] == 0.40                # 800 / 2000
    assert results["leverage"]["interest_coverage"] == 6.0          # 360 / 60

    # Profitability
    assert results["profitability"]["gross_margin_pct"] == 30.0     # 720 / 2400
    assert results["profitability"]["net_margin_pct"] == 10.0       # 240 / 2400
    assert results["profitability"]["roa_pct"] == 12.0              # 240 / 2000
    assert results["profitability"]["roe_pct"] == 20.0              # 240 / 1200

    # Efficiency
    assert results["efficiency"]["inventory_turnover"] == 16.0      # 2400 / 150
    assert results["efficiency"]["asset_turnover"] == 1.2           # 2400 / 2000
    # DSO: (200 * 365) / 2400 = 30.42 days
    assert results["efficiency"]["dso_days"] == pytest.approx(30.42, 0.05)

    # Altman Z
    assert results["altman_z"]["score"] is not None
    assert results["altman_z"]["zone"] in ["Safe Zone", "Grey Zone", "Distress Zone"]

    # Benchmark comparisons exist
    assert "current_ratio" in results["benchmark_comparisons"]
    assert "de_ratio" in results["benchmark_comparisons"]


def test_financial_ratios_zero_division_guard():
    """All zeros input must return safely without crashing."""
    zero_data = {
        "current_assets": 0,
        "current_liabilities": 0,
        "revenue": 0,
        "total_assets": 0,
        "total_debt": 0,
        "total_equity": 0
    }
    results = calculate_financial_ratios(zero_data, industry="Technology")
    assert results["liquidity"]["current_ratio"] is None
    assert results["leverage"]["de_ratio"] is None
    assert results["profitability"]["net_margin_pct"] is None
    assert results["altman_z"]["zone"] == "Unknown"
    assert isinstance(results["risk_flags"], list)


def test_financial_ratios_danger_flags():
    """Highly leveraged, unprofitable firm triggers appropriate risk flags."""
    distressed_data = {
        "current_assets": 100,
        "current_liabilities": 200,   # CR = 0.5 (< 1.0)
        "cash_and_equivalents": 10,
        "inventory": 50,
        "total_assets": 1000,
        "total_debt": 900,
        "total_equity": 100,          # D/E = 9.0 (> 3.0)
        "total_liabilities": 900,
        "revenue": 500,
        "gross_profit": 20,
        "net_profit": -150,           # Net margin < 0
        "ebit": -80,
        "interest_expense": 100,      # Interest coverage negative / < 1.5
        "retained_earnings": -300,
        "market_cap": 80
    }
    results = calculate_financial_ratios(distressed_data, industry="General")
    flags = results["risk_flags"]
    severities = [f["severity"] for f in flags]
    assert "critical" in severities
    assert any("Current ratio" in f["msg"] for f in flags)
    assert any("D/E ratio" in f["msg"] for f in flags)
    assert any("Net margin" in f["msg"] for f in flags)
