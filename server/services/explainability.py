"""
Explainable Risk Score Engine — RiskGuard Pro

Decomposes the composite Enterprise Risk & Health Score into explainable,
auditable domain components, factor contributions, and waterfall chart telemetry.
"""

from typing import Dict, Any, List


DOMAIN_WEIGHTS = {
    "Financial Solvency": 0.25,
    "Cybersecurity & Cloud": 0.20,
    "Operations & Supply Chain": 0.18,
    "Regulatory & Compliance": 0.15,
    "Market & Strategic": 0.12,
    "Human Capital": 0.10,
}


def explain_health_score(assessment_data: Dict[str, Any], ratios_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Decompose composite Enterprise Health Score into explainable domain contributions.
    """
    step_data = assessment_data.get("step_data", {}) if isinstance(assessment_data.get("step_data"), dict) else {}
    company_name = assessment_data.get("company_name", "Enterprise")
    target_health_score = float(assessment_data.get("health_score", 78.0))

    # Evaluate domain subscores (0 to 100, where 100 is pristine zero risk)
    # 1. Financial
    fin_deductions = []
    fin_subscore = 85.0
    if ratios_data:
        cr = ratios_data.get("liquidity", {}).get("current_ratio")
        if cr is not None and cr < 1.0:
            fin_subscore -= 30.0
            fin_deductions.append(f"Current ratio ({cr:.2f}) < 1.0 creates liquidity deficit")
        elif cr is not None and cr < 1.5:
            fin_subscore -= 15.0
            fin_deductions.append(f"Current ratio ({cr:.2f}) below 1.5 safety threshold")

        de = ratios_data.get("leverage", {}).get("de_ratio")
        if de is not None and de > 3.0:
            fin_subscore -= 25.0
            fin_deductions.append(f"D/E ratio ({de:.2f}) indicates severe leverage")
        elif de is not None and de > 1.5:
            fin_subscore -= 10.0
            fin_deductions.append(f"D/E ratio ({de:.2f}) exceeds industry median")

        alt = ratios_data.get("altman_z", {})
        if alt.get("zone") == "Distress Zone":
            fin_subscore -= 35.0
            fin_deductions.append(f"Altman Z-Score ({alt.get('score')}) in Distress Zone")
        elif alt.get("zone") == "Grey Zone":
            fin_subscore -= 15.0
            fin_deductions.append(f"Altman Z-Score ({alt.get('score')}) in Grey Zone")

    fin_subscore = max(10.0, min(100.0, fin_subscore))

    # 2. Cyber
    cyber_subscore = 80.0
    cyber_deductions = []
    q4 = step_data.get("step4", {})
    if str(q4.get("mfa_enabled", "true")).lower() == "false":
        cyber_subscore -= 25.0
        cyber_deductions.append("Absence of hardware/authenticator MFA on core endpoints")
    if str(q4.get("backup_frequency", "daily")).lower() in ["monthly", "rarely", "none"]:
        cyber_subscore -= 20.0
        cyber_deductions.append("Infrequent backup cycle increases ransomware exposure")
    cyber_subscore = max(10.0, min(100.0, cyber_subscore))

    # 3. Operations
    ops_subscore = 75.0
    ops_deductions = []
    q2 = step_data.get("step2", {})
    if str(q2.get("single_supplier", "false")).lower() == "true":
        ops_subscore -= 25.0
        ops_deductions.append("Critical single-source supplier concentration risk")
    ops_subscore = max(10.0, min(100.0, ops_subscore))

    # 4. Compliance
    comp_subscore = 88.0
    comp_deductions = []
    q5 = step_data.get("step5", {})
    if str(q5.get("regulatory_fines", "false")).lower() == "true":
        comp_subscore -= 30.0
        comp_deductions.append("Pending or historical regulatory non-compliance penalty")
    comp_subscore = max(10.0, min(100.0, comp_subscore))

    # 5. Market
    market_subscore = 78.0
    market_deductions = ["Macro demand fluctuation and sector competitive headwinds"]

    # 6. Human Capital
    hr_subscore = 82.0
    hr_deductions = ["Attrition in key engineering & quantitative analytics talent"]

    domain_breakdown = [
        {
            "domain": "Financial Solvency",
            "weight": 0.25,
            "subscore": round(fin_subscore, 1),
            "weighted_score": round(fin_subscore * 0.25, 2),
            "max_possible": 25.0,
            "points_lost": round(25.0 - (fin_subscore * 0.25), 2),
            "key_drivers": fin_deductions or ["Satisfactory liquidity buffers & capital structure"]
        },
        {
            "domain": "Cybersecurity & Cloud",
            "weight": 0.20,
            "subscore": round(cyber_subscore, 1),
            "weighted_score": round(cyber_subscore * 0.20, 2),
            "max_possible": 20.0,
            "points_lost": round(20.0 - (cyber_subscore * 0.20), 2),
            "key_drivers": cyber_deductions or ["Robust IAM controls and tested disaster recovery"]
        },
        {
            "domain": "Operations & Supply Chain",
            "weight": 0.18,
            "subscore": round(ops_subscore, 1),
            "weighted_score": round(ops_subscore * 0.18, 2),
            "max_possible": 18.0,
            "points_lost": round(18.0 - (ops_subscore * 0.18), 2),
            "key_drivers": ops_deductions or ["Multi-vendor redundancy across key delivery corridors"]
        },
        {
            "domain": "Regulatory & Compliance",
            "weight": 0.15,
            "subscore": round(comp_subscore, 1),
            "weighted_score": round(comp_subscore * 0.15, 2),
            "max_possible": 15.0,
            "points_lost": round(15.0 - (comp_subscore * 0.15), 2),
            "key_drivers": comp_deductions or ["Full statutory audit compliance & ISO governance"]
        },
        {
            "domain": "Market & Strategic",
            "weight": 0.12,
            "subscore": round(market_subscore, 1),
            "weighted_score": round(market_subscore * 0.12, 2),
            "max_possible": 12.0,
            "points_lost": round(12.0 - (market_subscore * 0.12), 2),
            "key_drivers": market_deductions
        },
        {
            "domain": "Human Capital",
            "weight": 0.10,
            "subscore": round(hr_subscore, 1),
            "weighted_score": round(hr_subscore * 0.10, 2),
            "max_possible": 10.0,
            "points_lost": round(10.0 - (hr_subscore * 0.10), 2),
            "key_drivers": hr_deductions
        }
    ]

    total_weighted = sum(d["weighted_score"] for d in domain_breakdown)
    total_lost = sum(d["points_lost"] for d in domain_breakdown)

    # Waterfall progression: Starts at 100 (Max Health) and subtracts points lost per domain
    running_total = 100.0
    waterfall_steps = [{"label": "Baseline Ideal (100)", "value": 100.0, "step_type": "base"}]
    for d in domain_breakdown:
        running_total -= d["points_lost"]
        waterfall_steps.append({
            "label": d["domain"],
            "delta": -d["points_lost"],
            "running_total": round(running_total, 1),
            "step_type": "deduction"
        })
    waterfall_steps.append({"label": "Final Score", "value": round(running_total, 1), "step_type": "total"})

    return {
        "company_name": company_name,
        "final_health_score": round(running_total, 1),
        "domains": domain_breakdown,
        "waterfall_steps": waterfall_steps,
        "primary_risk_driver": max(domain_breakdown, key=lambda d: d["points_lost"])["domain"],
        "total_points_deducted": round(total_lost, 1)
    }
