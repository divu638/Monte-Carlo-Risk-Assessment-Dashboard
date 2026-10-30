"""
Financial Ratios Engine & Altman Z-Score Calculator — RiskGuard Pro

Computes the institutional financial ratio suite from corporate financial statements:
1. 8 Main Essential Ratios (Current Ratio, Quick Ratio, Debt-to-Equity, Net Profit Margin,
   Operating Profit Margin, Interest Coverage, Inventory Turnover, Receivable Days)
2. Supporting Ratios across Liquidity, Solvency, Profitability, and Efficiency
3. Altman Z-Score with bankruptcy zone interpretation
4. Damodaran/BSE Industry Benchmarks & Quantitative Alert Flags
"""

import math

# ─── Industry Benchmarks ────────────────────────────────────────────────────────
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
    """Return numerator / denominator; fallback if denominator is zero or invalid."""
    try:
        if numerator is None or denominator is None:
            return fallback
        n = float(numerator)
        d = float(denominator)
        if d == 0.0 or math.isnan(d) or math.isnan(n) or math.isinf(d) or math.isinf(n):
            return fallback
        return n / d
    except (TypeError, ValueError, ZeroDivisionError):
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
    Altman Z-Score for private manufacturing / non-financial firms:
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
    Compute full financial ratio suite according to exact institutional accounting standards:
    8 Main Essential Ratios + Supporting Ratios across Liquidity, Solvency, Profitability, and Efficiency.
    """
    benchmarks = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["General"])

    def g(key, default=0.0):
        try:
            val = data.get(key)
            if val is None or val == "":
                return default
            fval = float(val)
            return fval if not (math.isnan(fval) or math.isinf(fval)) else default
        except (TypeError, ValueError):
            return default

    # Extract base figures
    revenue              = g("revenue")
    cogs                 = g("cogs")
    gross_profit         = g("gross_profit") or (revenue - cogs if revenue and cogs else 0.0)
    operating_expenses   = g("operating_expenses")
    ebit                 = g("ebit") or (gross_profit - operating_expenses if gross_profit and operating_expenses else 0.0)
    dna                  = g("depreciation_amortization")
    ebitda               = g("ebitda") or (ebit + dna if ebit and dna else ebit)
    interest_expense     = g("interest_expense")
    net_profit           = g("net_profit")
    
    current_assets       = g("current_assets")
    cash                 = g("cash_and_equivalents")
    st_investments       = g("short_term_investments")
    accounts_receivable  = g("accounts_receivable")
    inventory            = g("inventory")
    prepaid_expenses     = g("prepaid_expenses")
    
    current_liabilities  = g("current_liabilities")
    accounts_payable     = g("accounts_payable")
    
    total_debt           = g("total_debt")
    total_equity         = g("total_equity")
    total_liabilities    = g("total_liabilities") or total_debt
    total_assets         = g("total_assets")
    net_fixed_assets     = g("non_current_assets")
    
    credit_sales         = g("credit_sales") or revenue
    credit_purchases     = g("credit_purchases") or cogs
    avg_inventory        = g("avg_inventory") or inventory
    avg_receivables      = g("avg_receivables") or accounts_receivable
    avg_payables         = g("avg_payables") or accounts_payable
    avg_total_assets     = g("avg_total_assets") or total_assets
    avg_equity           = g("avg_equity") or total_equity
    
    retained_earnings    = g("retained_earnings")
    market_cap           = g("market_cap") or total_equity
    working_capital      = current_assets - current_liabilities
    capital_employed     = total_assets - current_liabilities
    avg_capital_employed = g("avg_capital_employed") or capital_employed
    
    cfo                  = g("operating_cash_flow") or (ebitda - g("tax_expense"))
    total_debt_service   = g("total_debt_service") or (interest_expense + g("principal_repayment"))

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. THE 8 MAIN ESSENTIAL RATIOS
    # ═══════════════════════════════════════════════════════════════════════════
    # 1. Current Ratio = Current Assets ÷ Current Liabilities
    current_ratio = _safe_div(current_assets, current_liabilities)

    # 2. Quick Ratio = (Current Assets − Inventory − Prepaid Expenses) ÷ Current Liabilities
    quick_assets = current_assets - inventory - prepaid_expenses
    quick_ratio = _safe_div(quick_assets, current_liabilities)

    # 3. Debt-to-Equity Ratio = Total Debt ÷ Shareholders' Equity
    de_ratio = _safe_div(total_debt, total_equity)

    # 4. Net Profit Margin = (Net Profit After Tax ÷ Net Revenue) × 100
    net_margin = _safe_div(net_profit, revenue)

    # 5. Operating Profit Margin = (EBIT ÷ Net Revenue) × 100
    operating_margin = _safe_div(ebit, revenue)

    # 6. Interest Coverage Ratio = EBIT ÷ Interest Expense
    interest_coverage = _safe_div(ebit, interest_expense) if interest_expense > 0 else None

    # 7. Inventory Turnover = COGS ÷ Average Inventory (fallback to inventory)
    inventory_turnover = _safe_div(cogs if cogs > 0 else revenue, avg_inventory) if avg_inventory > 0 else None

    # 8. Receivable Days = (Average Trade Receivables ÷ Net Credit Sales) × 365
    receivable_days = _safe_div(avg_receivables * 365, credit_sales if credit_sales > 0 else revenue) if (credit_sales > 0 or revenue > 0) else None

    # ═══════════════════════════════════════════════════════════════════════════
    # 2. SUPPORTING RATIOS
    # ═══════════════════════════════════════════════════════════════════════════
    # A. Liquidity Supporting
    cash_ratio = _safe_div(cash + st_investments, current_liabilities)
    wc_to_total_assets = _safe_div(working_capital, total_assets)

    # B. Solvency Supporting
    debt_to_assets = _safe_div(total_debt, total_assets)
    debt_ratio = _safe_div(total_liabilities, total_assets)  # for backward compatibility
    equity_ratio = _safe_div(total_equity, total_assets)
    debt_to_ebitda = _safe_div(total_debt, ebitda) if ebitda > 0 else None
    dscr = _safe_div(cfo, total_debt_service) if total_debt_service > 0 else None

    # C. Profitability Supporting
    gross_margin = _safe_div(gross_profit, revenue)
    roa = _safe_div(net_profit, avg_total_assets if avg_total_assets > 0 else total_assets)
    roe = _safe_div(net_profit, avg_equity if avg_equity > 0 else total_equity)
    roce = _safe_div(ebit, avg_capital_employed if avg_capital_employed > 0 else capital_employed)
    ebitda_margin = _safe_div(ebitda, revenue)
    expense_ratio = _safe_div(operating_expenses, revenue) if operating_expenses > 0 else None

    # D. Efficiency Supporting
    total_asset_turnover = _safe_div(revenue, avg_total_assets if avg_total_assets > 0 else total_assets)
    fixed_asset_turnover = _safe_div(revenue, net_fixed_assets) if net_fixed_assets > 0 else None
    receivables_turnover = _safe_div(credit_sales, avg_receivables) if avg_receivables > 0 else None
    payables_turnover = _safe_div(credit_purchases, avg_payables) if avg_payables > 0 else None
    payable_days = _safe_div(avg_payables * 365, credit_purchases) if credit_purchases > 0 else None
    inventory_days = _safe_div(avg_inventory * 365, cogs if cogs > 0 else revenue) if (cogs > 0 or revenue > 0) else None
    
    ccc_days = None
    if inventory_days is not None and receivable_days is not None:
        p_days = payable_days if payable_days is not None else 0.0
        ccc_days = inventory_days + receivable_days - p_days

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
        "asset_turnover":_benchmark_delta(total_asset_turnover, benchmarks.get("asset_turnover"), "Asset Turnover"),
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
        # 8 Main Essential Ratios directly at top level for easy access
        "main_ratios": {
            "current_ratio": {
                "name": "Current Ratio",
                "category": "Liquidity",
                "value": _round2(current_ratio),
                "formatted": f"{current_ratio:.2f}x" if current_ratio is not None else "N/A",
                "formula": "Current Assets ÷ Current Liabilities",
                "benchmark": benchmarks.get("current_ratio", 1.8)
            },
            "quick_ratio": {
                "name": "Quick Ratio",
                "category": "Liquidity",
                "value": _round2(quick_ratio),
                "formatted": f"{quick_ratio:.2f}x" if quick_ratio is not None else "N/A",
                "formula": "(Current Assets − Inventory − Prepaid Expenses) ÷ Current Liabilities",
                "benchmark": 1.0
            },
            "debt_to_equity": {
                "name": "Debt-to-Equity",
                "category": "Solvency",
                "value": _round2(de_ratio),
                "formatted": f"{de_ratio:.2f}x" if de_ratio is not None else "N/A",
                "formula": "Total Debt ÷ Shareholders' Equity",
                "benchmark": benchmarks.get("de_ratio", 1.0)
            },
            "net_profit_margin": {
                "name": "Net Profit Margin",
                "category": "Profitability",
                "value": _pct(net_margin),
                "formatted": f"{_pct(net_margin)}%" if net_margin is not None else "N/A",
                "formula": "(Net Profit After Tax ÷ Net Revenue) × 100",
                "benchmark": benchmarks.get("net_margin", 0.07) * 100
            },
            "operating_profit_margin": {
                "name": "Operating Profit Margin",
                "category": "Profitability",
                "value": _pct(operating_margin),
                "formatted": f"{_pct(operating_margin)}%" if operating_margin is not None else "N/A",
                "formula": "(EBIT ÷ Net Revenue) × 100",
                "benchmark": 12.0
            },
            "interest_coverage": {
                "name": "Interest Coverage Ratio",
                "category": "Debt Servicing",
                "value": _round2(interest_coverage),
                "formatted": f"{interest_coverage:.1f}x" if interest_coverage is not None else "N/A",
                "formula": "EBIT ÷ Interest Expense",
                "benchmark": 3.0
            },
            "inventory_turnover": {
                "name": "Inventory Turnover",
                "category": "Efficiency",
                "value": _round2(inventory_turnover),
                "formatted": f"{inventory_turnover:.1f}x" if inventory_turnover is not None else "N/A",
                "formula": "COGS ÷ Average Inventory",
                "benchmark": 6.0
            },
            "receivable_days": {
                "name": "Receivable Days (DSO)",
                "category": "Efficiency",
                "value": _round2(receivable_days),
                "formatted": f"{round(receivable_days)} days" if receivable_days is not None else "N/A",
                "formula": "(Average Trade Receivables ÷ Net Credit Sales) × 365",
                "benchmark": 45.0
            }
        },
        # Structured supporting categories preserving backward compatibility
        "liquidity": {
            "current_ratio":           _round2(current_ratio),
            "quick_ratio":             _round2(quick_ratio),
            "cash_ratio":              _round2(cash_ratio),
            "working_capital":          _round2(working_capital),
            "working_capital_to_assets": _pct(wc_to_total_assets),
        },
        "leverage": {
            "de_ratio":          _round2(de_ratio),
            "debt_ratio":        _round2(debt_ratio),
            "debt_to_assets":    _pct(debt_to_assets),
            "equity_ratio":      _pct(equity_ratio),
            "debt_to_ebitda":    _round2(debt_to_ebitda),
            "dscr":              _round2(dscr),
            "interest_coverage": _round2(interest_coverage),
        },
        "solvency": {
            "de_ratio":          _round2(de_ratio),
            "debt_to_assets":    _pct(debt_to_assets),
            "equity_ratio":      _pct(equity_ratio),
            "debt_to_ebitda":    _round2(debt_to_ebitda),
            "dscr":              _round2(dscr),
            "interest_coverage": _round2(interest_coverage),
        },
        "profitability": {
            "gross_margin_pct":      _pct(gross_margin),
            "operating_margin_pct":  _pct(operating_margin),
            "net_margin_pct":        _pct(net_margin),
            "ebitda_margin_pct":     _pct(ebitda_margin),
            "expense_ratio_pct":     _pct(expense_ratio),
            "roa_pct":               _pct(roa),
            "roe_pct":               _pct(roe),
            "roce_pct":              _pct(roce),
        },
        "efficiency": {
            "inventory_turnover":   _round2(inventory_turnover),
            "inventory_days":       _round2(inventory_days),
            "dso_days":             _round2(receivable_days),
            "receivable_days":      _round2(receivable_days),
            "receivables_turnover": _round2(receivables_turnover),
            "payable_days":         _round2(payable_days),
            "payables_turnover":    _round2(payables_turnover),
            "cash_conversion_cycle": _round2(ccc_days),
            "asset_turnover":       _round2(total_asset_turnover),
            "fixed_asset_turnover": _round2(fixed_asset_turnover),
        },
        "altman_z": altman,
        "benchmark_comparisons": comparisons,
        "risk_flags": flags,
        "industry": industry,
        "working_capital": _round2(working_capital),
    }
