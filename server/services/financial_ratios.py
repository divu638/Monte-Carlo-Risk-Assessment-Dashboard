"""
Financial Ratios Engine & Altman Z-Score Calculator — RiskGuard Pro

Computes all standard institutional financial ratios from raw balance sheet
and P&L inputs, with industry benchmark comparisons and Altman Z-Score.

Ratios Covered:
  Liquidity   : Current, Quick, Cash
  Leverage    : Debt-to-Equity, Debt Ratio, Interest Coverage
  Profitability: Gross Margin, Net Margin, ROA, ROE, EBITDA Margin
  Efficiency  : Inventory Turnover, Days Sales Outstanding (DSO), Asset Turnover
  Solvency    : Altman Z-Score (Safe / Grey / Distress zones)
"""

import math

# ─── Industry Benchmarks ────────────────────────────────────────────────────────
# Source: Damodaran / BSE sector averages (approximate)
INDUSTRY_BENCHMARKS = {
    "Manufacturing":   {"current_ratio": 1.8, "de_ratio": 0.9, "net_margin": 0.06, "roe": 0.12, "asset_turnover": 0.80},
    "Retail":          {"current_ratio": 1.4, "de_ratio": 1.2, "net_margin": 0.04, "roe": 0.15, "asset_turnover": 1.50},
    "Technology":      {"current_ratio": 2.5, "de_ratio": 0.4, "net_margin": 0.15, "roe": 0.20, "asset_turnover": 0.70},
    "Healthcare":      {"current_ratio": 2.1, "de_ratio": 0.6, "net_margin": 0.10, "roe": 0.14, "asset_turnover": 0.65},
    "Financial":       {"current_ratio": 1.2, "de_ratio": 5.0, "net_margin": 0.18, "roe": 0.12, "asset_turnover": 0.10},
    "Energy":          {"current_ratio": 1.5, "de_ratio": 1.3, "net_margin": 0.07, "roe": 0.10, "asset_turnover": 0.45},
    "General":         {"current_ratio": 1.8, "de_ratio": 1.0, "net_margin": 0.07, "roe": 0.12, "asset_turnover": 0.80},
}


def _safe_div(numerator, denominator, fallback=None):
    """Return numerator / denominator; fallback if denominator is zero or None."""
    try:
        n = float(numerator)
        d = float(denominator)
        if d == 0 or math.isnan(d) or math.isnan(n):
            return fallback
        return n / d
    except (TypeError, ValueError):
        return fallback


def _pct(value):
    """Round to 2 decimal places for percentage display."""
    return round(float(value) * 100, 2) if value is not None else None


def _round2(value):
    return round(float(value), 2) if value is not None else None


def _benchmark_delta(value, benchmark, label, higher_is_better=True):
    """Generate a human-readable benchmark comparison string."""
    if value is None or benchmark is None:
        return None
    delta_pct = ((value - benchmark) / abs(benchmark)) * 100 if benchmark != 0 else 0
    direction = "above" if delta_pct >= 0 else "below"
    sign = "+" if delta_pct >= 0 else ""
    sentiment = ""
    if higher_is_better:
        sentiment = "✅" if delta_pct >= -5 else "⚠️" if delta_pct >= -20 else "🔴"
    else:
        sentiment = "✅" if delta_pct <= 5 else "⚠️" if delta_pct <= 30 else "🔴"
    return f"{sentiment} {sign}{delta_pct:.1f}% {direction} industry avg ({benchmark})"


# ─── Altman Z-Score ─────────────────────────────────────────────────────────────

def calculate_altman_z(
    working_capital, total_assets, retained_earnings,
    ebit, market_cap, total_liabilities, revenue
):
    """
    Altman Z-Score for private manufacturing firms (1968 revised formula):
      Z = 1.2·X1 + 1.4·X2 + 3.3·X3 + 0.6·X4 + 0.999·X5

    Zones:
      Z > 2.99  → Safe Zone (financially healthy)
      1.81 ≤ Z ≤ 2.99 → Grey Zone (moderate distress risk)
      Z < 1.81  → Distress Zone (high bankruptcy risk)
    """
    if not total_assets or total_assets == 0:
        return {"score": None, "zone": "Unknown", "interpretation": "Insufficient data (total assets = 0)"}

    X1 = _safe_div(working_capital, total_assets, 0.0)               # Working Capital / Total Assets
    X2 = _safe_div(retained_earnings, total_assets, 0.0)             # Retained Earnings / Total Assets
    X3 = _safe_div(ebit, total_assets, 0.0)                          # EBIT / Total Assets
    X4 = _safe_div(market_cap, total_liabilities, 0.0) if total_liabilities else 0.0  # Mkt Cap / Total Liabilities
    X5 = _safe_div(revenue, total_assets, 0.0)                       # Revenue / Total Assets

    z = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 0.999 * X5

    if z > 2.99:
        zone = "Safe Zone"
        color = "success"
        interpretation = (
            f"Z-Score of {z:.2f} indicates financially robust operations with low bankruptcy probability. "
            f"Working capital efficiency (X1={X1:.3f}), earnings retention (X2={X2:.3f}), "
            f"and asset utilization (X5={X5:.3f}) are within safe thresholds."
        )
    elif z >= 1.81:
        zone = "Grey Zone"
        color = "warning"
        interpretation = (
            f"Z-Score of {z:.2f} places the entity in the Grey Zone — moderate financial stress. "
            f"Monitor EBIT/Assets ratio (X3={X3:.3f}) and debt coverage carefully. "
            f"Improvement in working capital management recommended."
        )
    else:
        zone = "Distress Zone"
        color = "danger"
        interpretation = (
            f"Z-Score of {z:.2f} signals significant financial distress. "
            f"Critical indicators: EBIT/Assets (X3={X3:.3f}), leverage (X4={X4:.3f}). "
            f"Immediate restructuring or capital infusion recommended."
        )

    return {
        "score": _round2(z),
        "zone": zone,
        "color": color,
        "interpretation": interpretation,
        "components": {
            "X1_working_capital_ratio": _round2(X1),
            "X2_retained_earnings_ratio": _round2(X2),
            "X3_ebit_asset_ratio": _round2(X3),
            "X4_market_equity_debt_ratio": _round2(X4),
            "X5_asset_turnover": _round2(X5),
        }
    }


# ─── Main Ratio Engine ───────────────────────────────────────────────────────────

def calculate_financial_ratios(data: dict, industry: str = "General") -> dict:
    """
    Compute full financial ratio suite from raw inputs.

    Expected keys in `data` (all in consistent currency units, e.g. ₹ Lakhs):
      current_assets, current_liabilities, cash_and_equivalents, inventory,
      total_assets, total_debt, total_equity, total_liabilities,
      revenue, gross_profit, net_profit, ebit, ebitda, interest_expense,
      accounts_receivable, retained_earnings, market_cap
    """
    benchmarks = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["General"])

    # Raw inputs — default zero-safe
    def g(key, default=0.0):
        try:
            val = float(data.get(key) or 0)
            return val if not (math.isnan(val) or math.isinf(val)) else default
        except (TypeError, ValueError):
            return default

    current_assets       = g("current_assets")
    current_liabilities  = g("current_liabilities")
    cash                 = g("cash_and_equivalents")
    inventory            = g("inventory")
    total_assets         = g("total_assets")
    total_debt           = g("total_debt")
    total_equity         = g("total_equity")
    total_liabilities    = g("total_liabilities") or total_debt
    revenue              = g("revenue")
    gross_profit         = g("gross_profit")
    net_profit           = g("net_profit")
    ebit                 = g("ebit")
    ebitda               = g("ebitda") or (ebit + g("depreciation_amortization"))
    interest_expense     = g("interest_expense")
    accounts_receivable  = g("accounts_receivable")
    retained_earnings    = g("retained_earnings")
    market_cap           = g("market_cap") or total_equity  # Proxy if not listed
    working_capital      = current_assets - current_liabilities

    # ── Liquidity Ratios ─────────────────────────────────────────────────────────
    current_ratio = _safe_div(current_assets, current_liabilities)
    quick_ratio   = _safe_div(current_assets - inventory, current_liabilities)
    cash_ratio    = _safe_div(cash, current_liabilities)

    # ── Leverage / Solvency Ratios ───────────────────────────────────────────────
    de_ratio         = _safe_div(total_debt, total_equity)
    debt_ratio       = _safe_div(total_liabilities, total_assets)
    interest_coverage = _safe_div(ebit, interest_expense) if interest_expense > 0 else None

    # ── Profitability Ratios ─────────────────────────────────────────────────────
    gross_margin  = _safe_div(gross_profit, revenue)
    net_margin    = _safe_div(net_profit, revenue)
    ebitda_margin = _safe_div(ebitda, revenue)
    roa           = _safe_div(net_profit, total_assets)
    roe           = _safe_div(net_profit, total_equity)

    # ── Efficiency Ratios ────────────────────────────────────────────────────────
    inventory_turnover = _safe_div(revenue, inventory) if inventory > 0 else None
    dso               = _safe_div(accounts_receivable * 365, revenue) if revenue > 0 else None
    asset_turnover     = _safe_div(revenue, total_assets)

    # ── Altman Z-Score ───────────────────────────────────────────────────────────
    altman = calculate_altman_z(
        working_capital, total_assets, retained_earnings,
        ebit, market_cap, total_liabilities, revenue
    )

    # ── Benchmark Comparisons ────────────────────────────────────────────────────
    comparisons = {
        "current_ratio": _benchmark_delta(current_ratio, benchmarks.get("current_ratio"), "Current Ratio"),
        "de_ratio":      _benchmark_delta(de_ratio, benchmarks.get("de_ratio"), "D/E Ratio", higher_is_better=False),
        "net_margin":    _benchmark_delta(net_margin, benchmarks.get("net_margin"), "Net Margin"),
        "roe":           _benchmark_delta(roe, benchmarks.get("roe"), "Return on Equity"),
        "asset_turnover":_benchmark_delta(asset_turnover, benchmarks.get("asset_turnover"), "Asset Turnover"),
    }

    # ── Risk Signal Flags ────────────────────────────────────────────────────────
    flags = []
    if current_ratio is not None and current_ratio < 1.0:
        flags.append({"severity": "critical", "msg": f"Current ratio {current_ratio:.2f} < 1.0 → Liquidity crisis risk."})
    elif current_ratio is not None and current_ratio < 1.5:
        flags.append({"severity": "high", "msg": f"Current ratio {current_ratio:.2f} below 1.5 → Monitor liquidity buffer."})

    if de_ratio is not None and de_ratio > 3.0:
        flags.append({"severity": "critical", "msg": f"D/E ratio {de_ratio:.2f} > 3.0 → Over-leveraged; credit risk elevated."})
    elif de_ratio is not None and de_ratio > benchmarks.get("de_ratio", 1.0) * 1.3:
        flags.append({"severity": "high", "msg": f"D/E ratio {de_ratio:.2f} is 30%+ above industry avg → Debt reduction advised."})

    if net_margin is not None and net_margin < 0:
        flags.append({"severity": "critical", "msg": f"Net margin {_pct(net_margin)}% < 0 → Net losses; immediate cost review required."})
    elif net_margin is not None and net_margin < benchmarks.get("net_margin", 0.05) * 0.5:
        flags.append({"severity": "high", "msg": f"Net margin {_pct(net_margin)}% is significantly below industry avg."})

    if interest_coverage is not None and interest_coverage < 1.5:
        flags.append({"severity": "critical", "msg": f"Interest coverage {interest_coverage:.2f}x < 1.5x → Unable to comfortably service debt."})
    elif interest_coverage is not None and interest_coverage < 3.0:
        flags.append({"severity": "medium", "msg": f"Interest coverage {interest_coverage:.2f}x — tight; monitor cash flow."})

    if altman.get("zone") == "Distress Zone":
        flags.append({"severity": "critical", "msg": f"Altman Z-Score {altman['score']} in DISTRESS zone → High bankruptcy probability."})
    elif altman.get("zone") == "Grey Zone":
        flags.append({"severity": "high", "msg": f"Altman Z-Score {altman['score']} in GREY zone → Monitor financial health closely."})

    return {
        "liquidity": {
            "current_ratio":  _round2(current_ratio),
            "quick_ratio":    _round2(quick_ratio),
            "cash_ratio":     _round2(cash_ratio),
            "working_capital": _round2(working_capital),
        },
        "leverage": {
            "de_ratio":          _round2(de_ratio),
            "debt_ratio":        _round2(debt_ratio),
            "interest_coverage": _round2(interest_coverage),
        },
        "profitability": {
            "gross_margin_pct":  _pct(gross_margin),
            "net_margin_pct":    _pct(net_margin),
            "ebitda_margin_pct": _pct(ebitda_margin),
            "roa_pct":           _pct(roa),
            "roe_pct":           _pct(roe),
        },
        "efficiency": {
            "inventory_turnover": _round2(inventory_turnover),
            "dso_days":           _round2(dso),
            "asset_turnover":     _round2(asset_turnover),
        },
        "altman_z": altman,
        "benchmark_comparisons": comparisons,
        "risk_flags": flags,
        "industry": industry,
        "working_capital": _round2(working_capital),
    }
