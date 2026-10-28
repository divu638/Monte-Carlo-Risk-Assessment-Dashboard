"""
Rule-Based Solutions & ISO 31000 Mitigation Engine — RiskGuard Pro

Evaluates calculated financial ratios, Altman Z-Score, operational questions,
and cyber metrics to generate institutional, actionable 3-tier treatment plans.
Complies with ISO 31000:2018 Risk Management Guidelines (Avoid, Reduce, Transfer, Accept).
"""

from typing import List, Dict, Any


def evaluate_rules(ratios: Dict[str, Any], cyber_data: Dict[str, Any] = None, operational_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Evaluate domain-specific risk rules and return prioritized, structured mitigation solutions.
    """
    solutions = []

    # ── 1. LIQUIDITY & WORKING CAPITAL RULES ─────────────────────────────────────
    liquidity = ratios.get("liquidity", {})
    cr = liquidity.get("current_ratio")
    qr = liquidity.get("quick_ratio")

    if cr is not None and cr < 1.0:
        solutions.append({
            "rule_id": "LIQ-001",
            "category": "Financial",
            "title": "Immediate Working Capital Emergency Stabilization",
            "severity": "Critical",
            "treatment_type": "Reduce",
            "priority": "P1 - Critical Immediate",
            "tier": "Tier 1: 0-30 Days (Immediate Containment)",
            "timeline": "0-30 Days",
            "cost_range": "₹1.5 Lakhs – ₹4.0 Lakhs",
            "expected_risk_reduction_pct": 45,
            "condition": f"Current Ratio ({cr:.2f}) < 1.0 (Negative Net Working Capital)",
            "actions": [
                "Establish weekly rolling cash-flow forecasting ledger and freeze discretionary CAPEX.",
                "Initiate invoice discounting or factoring for receivables aged over 30 days.",
                "Renegotiate payment terms with top 5 suppliers to stretch payables to 45-60 days.",
                "Secure emergency revolving credit line or short-term bridge facility from existing banker."
            ]
        })
    elif cr is not None and cr < 1.5:
        solutions.append({
            "rule_id": "LIQ-002",
            "category": "Financial",
            "title": "Working Capital Buffer Reinforcement",
            "severity": "High",
            "treatment_type": "Reduce",
            "priority": "P2 - High Priority",
            "tier": "Tier 2: 30-90 Days (Preventive Engineering)",
            "timeline": "30-90 Days",
            "cost_range": "₹80,000 – ₹2.5 Lakhs",
            "expected_risk_reduction_pct": 30,
            "condition": f"Current Ratio ({cr:.2f}) < 1.5 (Tight Liquidity Cushion)",
            "actions": [
                "Streamline order-to-cash cycle to accelerate milestone billing.",
                "Conduct quarterly inventory rationalization to unlock dormant working capital.",
                "Establish minimum liquidity threshold buffer equal to 45 days of OPEX."
            ]
        })

    # ── 2. LEVERAGE & SOLVENCY RULES ─────────────────────────────────────────────
    leverage = ratios.get("leverage", {})
    de = leverage.get("de_ratio")
    ic = leverage.get("interest_coverage")

    if de is not None and de > 3.0:
        solutions.append({
            "rule_id": "LEV-001",
            "category": "Financial",
            "title": "Capital Structure De-leveraging & Debt Restructuring",
            "severity": "Critical",
            "treatment_type": "Avoid",
            "priority": "P1 - Critical Immediate",
            "tier": "Tier 1: 0-30 Days (Immediate Containment)",
            "timeline": "0-60 Days",
            "cost_range": "₹3.0 Lakhs – ₹10.0 Lakhs",
            "expected_risk_reduction_pct": 50,
            "condition": f"Debt-to-Equity Ratio ({de:.2f}) > 3.0 (Severe Over-Leverage)",
            "actions": [
                "Engage senior lenders to negotiate covenant relaxations and tenure extensions.",
                "Assess asset sale leaseback options for non-core real estate or machinery.",
                "Evaluate promoter equity infusion or subordinated debt conversion.",
                "Place moratorium on debt-funded expansion projects until D/E drops below 2.0x."
            ]
        })

    if ic is not None and ic < 1.5:
        solutions.append({
            "rule_id": "LEV-002",
            "category": "Financial",
            "title": "Debt Service Coverage Shield & Interest Rate Hedging",
            "severity": "Critical",
            "treatment_type": "Transfer",
            "priority": "P1 - Critical Immediate",
            "tier": "Tier 2: 30-90 Days (Preventive Engineering)",
            "timeline": "30-90 Days",
            "cost_range": "₹1.0 Lakhs – ₹3.5 Lakhs",
            "expected_risk_reduction_pct": 40,
            "condition": f"Interest Coverage ({ic:.2f}x) < 1.5x (Debt Servicing Fragility)",
            "actions": [
                "Refinance high-coupon short-term borrowings into lower-cost term facilities.",
                "Execute interest rate caps or fixed-rate swaps to mitigate rate hike shocks.",
                "Direct free cash flow priority to prepay highest interest tranches."
            ]
        })

    # ── 3. ALTMAN Z-SCORE SOLVENCY RULES ─────────────────────────────────────────
    altman = ratios.get("altman_z", {})
    z_zone = altman.get("zone")
    z_score = altman.get("score")

    if z_zone == "Distress Zone":
        solutions.append({
            "rule_id": "ALT-001",
            "category": "Governance",
            "title": "Turnaround Solvency & Board Escalation Protocol",
            "severity": "Critical",
            "treatment_type": "Avoid",
            "priority": "P1 - Critical Immediate",
            "tier": "Tier 1: 0-30 Days (Immediate Containment)",
            "timeline": "0-30 Days",
            "cost_range": "₹5.0 Lakhs – ₹15.0 Lakhs",
            "expected_risk_reduction_pct": 60,
            "condition": f"Altman Z-Score ({z_score}) in DISTRESS ZONE (High Bankruptcy Risk)",
            "actions": [
                "Convene special Board Audit Committee session with statutory restructuring advisors.",
                "Conduct comprehensive operational forensic review of negative margin business units.",
                "Implement strict zero-based budgeting across all corporate divisions.",
                "Institute 13-week direct cash flow forecasting updated daily."
            ]
        })
    elif z_zone == "Grey Zone":
        solutions.append({
            "rule_id": "ALT-002",
            "category": "Governance",
            "title": "Proactive Enterprise Resilience & Margin Recovery",
            "severity": "High",
            "treatment_type": "Reduce",
            "priority": "P2 - High Priority",
            "tier": "Tier 2: 30-90 Days (Preventive Engineering)",
            "timeline": "30-90 Days",
            "cost_range": "₹1.5 Lakhs – ₹5.0 Lakhs",
            "expected_risk_reduction_pct": 35,
            "condition": f"Altman Z-Score ({z_score}) in GREY ZONE (Moderate Vulnerability)",
            "actions": [
                "Conduct customer profitability analysis to weed out margin-dilutive contracts.",
                "Implement supply chain cost rationalization across top spending categories.",
                "Enhance retained earnings retention by pausing executive dividend distributions."
            ]
        })

    # ── 4. EFFICIENCY & RECEIVABLES RULES ─────────────────────────────────────────
    efficiency = ratios.get("efficiency", {})
    dso = efficiency.get("dso_days")
    if dso is not None and dso > 60:
        solutions.append({
            "rule_id": "EFF-001",
            "category": "Operational",
            "title": "Receivables Aging Acceleration & Credit Risk Controls",
            "severity": "Medium",
            "treatment_type": "Reduce",
            "priority": "P3 - Medium Priority",
            "tier": "Tier 2: 30-90 Days (Preventive Engineering)",
            "timeline": "30-90 Days",
            "cost_range": "₹50,000 – ₹1.8 Lakhs",
            "expected_risk_reduction_pct": 25,
            "condition": f"Days Sales Outstanding ({dso:.1f} days) > 60 Days (Slow Cash Collection)",
            "actions": [
                "Deploy automated dunning and ERP receivables alerts at 15/30/45 days overdue.",
                "Introduce 1.5% prompt payment cash discounts for payments cleared within 10 days.",
                "Impose strict credit limits on counterparties with history of delayed settlement."
            ]
        })

    # ── 5. CYBERSECURITY POSTURE RULES ───────────────────────────────────────────
    if cyber_data:
        mfa_enabled = cyber_data.get("mfa_enabled", False)
        backup_frequency = cyber_data.get("backup_frequency", "daily")
        vuln_score = float(cyber_data.get("vulnerability_score", 3.0))

        if not mfa_enabled or vuln_score > 6.0:
            solutions.append({
                "rule_id": "CYB-001",
                "category": "Cybersecurity",
                "title": "Zero-Trust Identity & Critical Perimeter Hardening",
                "severity": "Critical",
                "treatment_type": "Reduce",
                "priority": "P1 - Critical Immediate",
                "tier": "Tier 1: 0-30 Days (Immediate Containment)",
                "timeline": "0-30 Days",
                "cost_range": "₹1.2 Lakhs – ₹3.5 Lakhs",
                "expected_risk_reduction_pct": 55,
                "condition": f"High Cyber Vulnerability (Score: {vuln_score}/10, MFA: {mfa_enabled})",
                "actions": [
                    "Enforce mandatory hardware-token or authenticator MFA across all SSO and VPN entry points.",
                    "Isolate critical database endpoints behind zero-trust private network tunnels.",
                    "Perform automated perimeter port scan and patch all CVSS 7.0+ external vulnerabilities.",
                    "Execute immutable, air-gapped daily database backups tested with weekly restore drills."
                ]
            })

    # Default fallback solutions if financials are healthy
    if not solutions:
        solutions.append({
            "rule_id": "GOV-001",
            "category": "Governance",
            "title": "Continuous Enterprise Risk Governance & ISO 31000 Audit",
            "severity": "Low",
            "treatment_type": "Accept",
            "priority": "P4 - Routine Governance",
            "tier": "Tier 3: 90+ Days (Ongoing Governance)",
            "timeline": "90+ Days",
            "cost_range": "₹50,000 – ₹1.2 Lakhs",
            "expected_risk_reduction_pct": 15,
            "condition": "Enterprise ratios satisfy standard baseline safety margins",
            "actions": [
                "Maintain quarterly Board risk committee presentations with Monte Carlo VaR updates.",
                "Review business continuity and supplier SLA agreements semi-annually.",
                "Conduct annual independent statutory IT security and financial audits."
            ]
        })

    # Sort by priority (P1 first, then P2, P3, P4)
    priority_order = {"P1 - Critical Immediate": 1, "P2 - High Priority": 2, "P3 - Medium Priority": 3, "P4 - Routine Governance": 4}
    solutions.sort(key=lambda s: priority_order.get(s.get("priority"), 5))
    return solutions
