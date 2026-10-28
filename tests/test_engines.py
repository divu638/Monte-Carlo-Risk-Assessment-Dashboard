"""
Test Suite: Enterprise Risk Services (Rule Engine, Stress Testing, Explainability, Cyber Module)
Verifies:
- Rule-based ISO 31000 solutions generation and priority ordering
- Stress testing scenarios and shock application
- Explainable risk score domain decomposition and waterfall math
- Cybersecurity CVSS posture scoring and Monte Carlo feed parameters
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))
from services.rule_engine import evaluate_rules
from services.stress_testing import run_stress_test, PRESET_SCENARIOS
from services.explainability import explain_health_score
from services.cyber_engine import calculate_cyber_posture


def test_rule_engine_critical_liquidity():
    """Verify Current Ratio < 1.0 triggers P1 Critical working capital rule."""
    ratios = {
        "liquidity": {"current_ratio": 0.85, "quick_ratio": 0.5},
        "leverage": {"de_ratio": 1.2, "interest_coverage": 4.0},
        "altman_z": {"zone": "Safe Zone", "score": 3.2}
    }
    solutions = evaluate_rules(ratios)
    assert len(solutions) > 0
    rule_ids = [s["rule_id"] for s in solutions]
    assert "LIQ-001" in rule_ids
    liq_rule = next(s for s in solutions if s["rule_id"] == "LIQ-001")
    assert liq_rule["severity"] == "Critical"
    assert liq_rule["treatment_type"] == "Reduce"
    assert "actions" in liq_rule and len(liq_rule["actions"]) >= 3


def test_rule_engine_altman_distress():
    """Verify Altman Z in Distress Zone triggers P1 Solvency turnaround rule."""
    ratios = {
        "liquidity": {"current_ratio": 1.6},
        "leverage": {"de_ratio": 3.5},
        "altman_z": {"zone": "Distress Zone", "score": 1.4}
    }
    solutions = evaluate_rules(ratios)
    rule_ids = [s["rule_id"] for s in solutions]
    assert "ALT-001" in rule_ids
    assert "LEV-001" in rule_ids


def test_stress_testing_recession_scenario():
    """Verify recession scenario degrades health score and increases VaR."""
    base_fin = {
        "revenue": 10_000_000,
        "total_debt": 3_000_000,
        "total_equity": 7_000_000,
        "total_assets": 10_000_000,
        "current_assets": 4_000_000,
        "current_liabilities": 2_000_000,
        "net_profit": 1_200_000,
        "ebit": 1_800_000
    }
    scen = PRESET_SCENARIOS["recession"]
    res = run_stress_test(
        base_financials=base_fin,
        base_health_score=85.0,
        base_var_exposure=1_200_000.0,
        revenue_shock_pct=scen["revenue_shock_pct"],
        debt_increase_pct=scen["debt_increase_pct"],
        cost_inflation_pct=scen["cost_inflation_pct"]
    )
    assert res["stressed_metrics"]["health_score"] < 85.0
    assert res["stressed_metrics"]["var_95"] >= 1_200_000.0
    assert "stressed_ratios" in res
    assert "altman_zone" in res


def test_explainable_score_waterfall():
    """Verify waterfall math: baseline 100 minus point deductions equals final score."""
    assessment = {
        "company_name": "TestCorp Industries",
        "health_score": 75.0,
        "step_data": {
            "step4": {"mfa_enabled": "false", "backup_frequency": "rarely"},
            "step2": {"single_supplier": "true"}
        }
    }
    ratios = {
        "liquidity": {"current_ratio": 1.2},
        "leverage": {"de_ratio": 2.2},
        "altman_z": {"zone": "Grey Zone", "score": 2.4}
    }
    explanation = explain_health_score(assessment, ratios)
    assert len(explanation["domains"]) == 6
    assert "waterfall_steps" in explanation
    assert explanation["primary_risk_driver"] in [d["domain"] for d in explanation["domains"]]

    # Verify waterfall endpoints
    steps = explanation["waterfall_steps"]
    assert steps[0]["value"] == 100.0
    assert steps[-1]["value"] == explanation["final_health_score"]


def test_cyber_posture_cvss_calculation():
    """Verify CVSS score, threat tier, and Monte Carlo feeding outputs."""
    inputs = {
        "ransomware_resilience": 4.0,
        "data_breach_prevention": 5.0,
        "vulnerability_exposure": 7.0,  # High vulnerability
        "access_control_iam": 4.0,
        "backup_recovery": 5.0,
        "annual_revenue": 50_000_000
    }
    res = calculate_cyber_posture(inputs)
    assert 0.0 <= res["cvss_composite_score"] <= 10.0
    assert res["threat_tier"] in ["Moderate Exposure", "Elevated Threat", "Critical Vulnerability"]
    assert res["annual_breach_probability"] > 0.2
    assert res["single_loss_expectancy"] > 0
    assert "monte_carlo_feed" in res
    assert 1 <= res["monte_carlo_feed"]["likelihood_equivalent"] <= 5
    assert len(res["nist_recommendations"]) > 0
