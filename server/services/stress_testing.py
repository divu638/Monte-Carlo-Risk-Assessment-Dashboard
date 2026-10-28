"""
Quantitative Stress Testing & What-If Scenario Engine — RiskGuard Pro

Simulates macroeconomic shocks and cyber threat surges across:
1. Financial solvency & ratio deterioration
2. Altman Z-Score distress migration
3. Vectorized Monte Carlo VaR recalculation
4. Enterprise Health Score impact telemetry
"""

import copy
import numpy as np
from services.financial_ratios import calculate_financial_ratios, calculate_altman_z

PRESET_SCENARIOS = {
    "recession": {
        "name": "Severe Macroeconomic Recession",
        "description": "Global demand contraction, 25% revenue collapse, credit tightening with 20% debt expansion.",
        "revenue_shock_pct": -25.0,
        "debt_increase_pct": 20.0,
        "cost_inflation_pct": 5.0,
        "cyber_multiplier": 1.0,
        "dso_extension_days": 25.0,
        "extra_loss_outlay": 0.0
    },
    "supply_chain": {
        "name": "Global Supply Chain Paralysis",
        "description": "Port logjams, 30% logistics & raw material cost surge, +45 days working capital collection delay.",
        "revenue_shock_pct": -10.0,
        "debt_increase_pct": 10.0,
        "cost_inflation_pct": 30.0,
        "cyber_multiplier": 1.2,
        "dso_extension_days": 45.0,
        "extra_loss_outlay": 0.0
    },
    "ransomware": {
        "name": "Enterprise Ransomware & Cloud Blackout",
        "description": "Double-extortion cyber attack, 3x cyber incident surge, ₹5 Cr recovery & downtime outlay.",
        "revenue_shock_pct": -15.0,
        "debt_increase_pct": 5.0,
        "cost_inflation_pct": 10.0,
        "cyber_multiplier": 3.0,
        "dso_extension_days": 15.0,
        "extra_loss_outlay": 50000000.0  # ₹5 Crore downtime outlay
    },
    "stagflation": {
        "name": "Stagflation & Interest Rate Shock",
        "description": "Simultaneous inflation surge (20%), 300 bps interest rate hike, and stagnant 15% revenue drop.",
        "revenue_shock_pct": -15.0,
        "debt_increase_pct": 15.0,
        "cost_inflation_pct": 20.0,
        "cyber_multiplier": 1.1,
        "dso_extension_days": 30.0,
        "extra_loss_outlay": 0.0
    }
}


def run_stress_test(
    base_financials: dict,
    base_health_score: float = 78.0,
    base_var_exposure: float = 1450000.0,
    revenue_shock_pct: float = 0.0,
    debt_increase_pct: float = 0.0,
    cost_inflation_pct: float = 0.0,
    cyber_multiplier: float = 1.0,
    dso_extension_days: float = 0.0,
    extra_loss_outlay: float = 0.0,
    industry: str = "General",
    iterations: int = 5000
) -> dict:
    """
    Apply stress multipliers to base financials and compute stressed metrics.
    """
    # Clone base financials
    f = copy.deepcopy(base_financials or {})

    rev = float(f.get("revenue", 10000000.0))
    debt = float(f.get("total_debt", 4000000.0))
    equity = float(f.get("total_equity", 6000000.0))
    assets = float(f.get("total_assets", 10000000.0))
    c_assets = float(f.get("current_assets", 3000000.0))
    c_liab = float(f.get("current_liabilities", 2000000.0))
    net_profit = float(f.get("net_profit", 1000000.0))
    ebit = float(f.get("ebit", 1500000.0))
    receivables = float(f.get("accounts_receivable", 1200000.0))

    # Apply shocks
    stressed_rev = max(0.0, rev * (1.0 + revenue_shock_pct / 100.0))
    rev_delta = stressed_rev - rev

    stressed_debt = debt * (1.0 + debt_increase_pct / 100.0)
    debt_delta = stressed_debt - debt

    # Net profit is hit by revenue collapse and cost inflation
    cost_hit = (rev - net_profit) * (cost_inflation_pct / 100.0)
    stressed_profit = net_profit + rev_delta - cost_hit - (extra_loss_outlay * 0.2)
    stressed_ebit = max(0.0, ebit + rev_delta - cost_hit)

    # Cash / Working capital reduction from debt and profit hit
    stressed_c_assets = max(0.0, c_assets + (rev_delta * 0.4) - (cost_hit * 0.3))
    stressed_c_liab = c_liab + (debt_delta * 0.3)
    stressed_assets = max(1.0, assets + rev_delta - (cost_hit * 0.5))
    stressed_equity = max(1.0, equity + (stressed_profit - net_profit))

    stressed_data = {
        "revenue": stressed_rev,
        "total_debt": stressed_debt,
        "total_equity": stressed_equity,
        "total_assets": stressed_assets,
        "current_assets": stressed_c_assets,
        "current_liabilities": stressed_c_liab,
        "total_liabilities": stressed_debt,
        "gross_profit": max(0.0, float(f.get("gross_profit", rev * 0.35)) + rev_delta * 0.5),
        "net_profit": stressed_profit,
        "ebit": stressed_ebit,
        "ebitda": max(0.0, stressed_ebit * 1.25),
        "interest_expense": float(f.get("interest_expense", 300000.0)) * (1.0 + debt_increase_pct / 100.0),
        "accounts_receivable": receivables * (1.0 + dso_extension_days / 90.0),
        "retained_earnings": float(f.get("retained_earnings", 2000000.0)) + min(0.0, stressed_profit),
        "market_cap": max(100000.0, float(f.get("market_cap", equity)) * (1.0 + min(0.0, revenue_shock_pct * 1.2 / 100.0))),
        "inventory": float(f.get("inventory", 800000.0))
    }

    # Recalculate financial ratios & Altman Z
    ratios = calculate_financial_ratios(stressed_data, industry=industry)

    # Stressed Health Score (0-100)
    score_penalty = 0.0
    if revenue_shock_pct < 0:
        score_penalty += abs(revenue_shock_pct) * 0.6
    if debt_increase_pct > 0:
        score_penalty += debt_increase_pct * 0.4
    if cost_inflation_pct > 0:
        score_penalty += cost_inflation_pct * 0.3
    if cyber_multiplier > 1.0:
        score_penalty += (cyber_multiplier - 1.0) * 8.0
    if extra_loss_outlay > 0:
        score_penalty += 12.0

    stressed_health_score = max(10.0, min(100.0, round(base_health_score - score_penalty, 1)))

    # Vectorized Monte Carlo VaR under stress
    # Higher volatility and higher frequency under stress
    np.random.seed(42)
    p_event = min(0.95, 0.35 * cyber_multiplier * (1.0 + abs(revenue_shock_pct) / 100.0))
    sigma = 1.2 + (cost_inflation_pct / 100.0)
    base_loss = base_var_exposure * (1.0 + (debt_increase_pct + abs(revenue_shock_pct)) / 100.0) + extra_loss_outlay

    events = np.random.binomial(1, p_event, iterations)
    severities = np.random.lognormal(mean=np.log(max(1.0, base_loss * 0.3)), sigma=sigma, size=iterations)
    simulated_losses = events * severities

    stressed_mean_loss = float(np.mean(simulated_losses))
    stressed_var_95 = float(np.percentile(simulated_losses, 95))
    stressed_worst_case = float(np.max(simulated_losses))

    return {
        "shocks_applied": {
            "revenue_shock_pct": revenue_shock_pct,
            "debt_increase_pct": debt_increase_pct,
            "cost_inflation_pct": cost_inflation_pct,
            "cyber_multiplier": cyber_multiplier,
            "dso_extension_days": dso_extension_days,
            "extra_loss_outlay": extra_loss_outlay
        },
        "base_metrics": {
            "health_score": base_health_score,
            "var_95": base_var_exposure
        },
        "stressed_metrics": {
            "health_score": stressed_health_score,
            "health_score_delta": round(stressed_health_score - base_health_score, 1),
            "mean_loss": round(stressed_mean_loss, 2),
            "var_95": round(stressed_var_95, 2),
            "worst_case": round(stressed_worst_case, 2),
            "var_increase_pct": round(((stressed_var_95 - base_var_exposure) / max(1.0, base_var_exposure)) * 100, 1)
        },
        "stressed_ratios": ratios,
        "altman_zone": ratios["altman_z"]["zone"],
        "altman_score": ratios["altman_z"]["score"]
    }
