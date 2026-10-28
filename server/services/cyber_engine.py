"""
Cybersecurity Risk & Threat Posture Engine — RiskGuard Pro

Evaluates CVSS-style 0-10 threat scores across 5 core security vectors:
1. Ransomware Resilience & Air-gapping
2. Data Breach Prevention & Cryptography
3. Vulnerability Exposure & Patch Velocity
4. Identity & Access Management (IAM / MFA)
5. Disaster Recovery & Backup Posture

Feeds quantitative probability and loss distributions into the Monte Carlo VaR simulator.
"""

from typing import Dict, Any


def calculate_cyber_posture(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute comprehensive cyber risk posture and quantitative loss parameters.
    """
    def s(key, default=5.0):
        try:
            val = float(inputs.get(key, default))
            return max(0.0, min(10.0, val))
        except (TypeError, ValueError):
            return default

    ransomware     = s("ransomware_resilience", 6.5)
    breach         = s("data_breach_prevention", 7.0)
    vulnerability  = s("vulnerability_exposure", 4.0)  # Lower is safer
    access_control = s("access_control_iam", 7.5)
    backup_posture = s("backup_recovery", 8.0)

    # Convert resilience scores to 0-10 threat impact (where 10 is highest threat)
    threat_ransomware    = 10.0 - ransomware
    threat_breach        = 10.0 - breach
    threat_vulnerability = vulnerability  # Already exposure
    threat_iam           = 10.0 - access_control
    threat_backup        = 10.0 - backup_posture

    # Composite CVSS-style threat score (0.0 to 10.0)
    cvss_score = round(
        (threat_ransomware * 0.30) +
        (threat_breach * 0.25) +
        (threat_vulnerability * 0.20) +
        (threat_iam * 0.15) +
        (threat_backup * 0.10),
        1
    )

    # Cyber Posture Index (0 - 100, 100 is impenetrable)
    posture_index = round(100.0 - (cvss_score * 10.0), 1)

    if cvss_score < 3.0:
        threat_tier = "Hardened Defense"
        tier_color = "success"
        annual_breach_prob = 0.05
    elif cvss_score < 6.0:
        threat_tier = "Moderate Exposure"
        tier_color = "warning"
        annual_breach_prob = 0.22
    elif cvss_score < 8.0:
        threat_tier = "Elevated Threat"
        tier_color = "danger"
        annual_breach_prob = 0.55
    else:
        threat_tier = "Critical Vulnerability"
        tier_color = "danger"
        annual_breach_prob = 0.85

    # Quantitative Financial VaR parameters for Monte Carlo feeding
    # Single Loss Expectancy (SLE): Ransomware + extortion + forensic + legal + downtime
    annual_revenue = float(inputs.get("annual_revenue", 250000000.0))  # ₹25 Cr default
    estimated_sle = round(annual_revenue * (0.02 + (cvss_score / 100.0)), 2)
    annualized_loss_expectancy = round(estimated_sle * annual_breach_prob, 2)

    # NIST Cybersecurity Framework (CSF 2.0) recommendations
    nist_recommendations = []
    if threat_ransomware > 4.0:
        nist_recommendations.append({
            "function": "PROTECT & RECOVER",
            "action": "Deploy immutable, air-gapped backups (WORM storage) with 4-hour RTO verification.",
            "cvss_impact": "-1.5 pts"
        })
    if threat_iam > 4.0:
        nist_recommendations.append({
            "function": "IDENTIFY & PROTECT",
            "action": "Enforce FIDO2/WebAuthn hardware MFA across all administrative and SSH jump boxes.",
            "cvss_impact": "-1.2 pts"
        })
    if threat_vulnerability > 5.0:
        nist_recommendations.append({
            "function": "DETECT & RESPOND",
            "action": "Implement automated daily external vulnerability scanning and 14-day SLA for critical CVEs.",
            "cvss_impact": "-1.0 pts"
        })
    if threat_breach > 4.0:
        nist_recommendations.append({
            "function": "PROTECT",
            "action": "Encrypt all PII and customer financial databases with AES-256 and client-side envelope keys.",
            "cvss_impact": "-0.8 pts"
        })

    return {
        "cvss_composite_score": cvss_score,
        "posture_index": posture_index,
        "threat_tier": threat_tier,
        "tier_color": tier_color,
        "annual_breach_probability": annual_breach_prob,
        "single_loss_expectancy": estimated_sle,
        "annualized_loss_expectancy": annualized_loss_expectancy,
        "vectors": {
            "ransomware_defense": {"score": ransomware, "threat": round(threat_ransomware, 1)},
            "data_breach_prevention": {"score": breach, "threat": round(threat_breach, 1)},
            "vulnerability_management": {"score": round(10.0 - vulnerability, 1), "threat": vulnerability},
            "access_control_iam": {"score": access_control, "threat": round(threat_iam, 1)},
            "disaster_recovery": {"score": backup_posture, "threat": round(threat_backup, 1)}
        },
        "nist_recommendations": nist_recommendations,
        "monte_carlo_feed": {
            "likelihood_equivalent": min(5, max(1, int(round(cvss_score / 2.0)))),
            "impact_equivalent": min(5, max(1, int(round(estimated_sle / (annual_revenue * 0.02))))),
            "event_probability": annual_breach_prob,
            "base_loss_amount": estimated_sle
        }
    }
