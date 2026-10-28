"""
RiskGuard Pro — Enterprise Demo Data & Baseline Seeder
Executes idempotent database population for development, evaluation, and live demonstration:
1. Demo Admin (CRO) & User (Lead Analyst) credentials
2. Enterprise 5-Pillar Risk Registry dataset with financial exposures
3. Industry financial ratio benchmarks (Damodaran sectoral baselines)
4. Baseline assessment submission with full P&L and Balance Sheet telemetry
5. ISO 31000 Action Tracker mitigation tasks
"""

import os
import sys
import json
from datetime import datetime, timezone

# Add server directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "server")))
import database

DEMO_USERS = [
    {
        "firstname": "Chief Risk",
        "lastname": "Officer (CRO)",
        "company": "RiskGuard Global Enterprise",
        "email": "admin@riskguard.internal",
        "password": "Admin@RiskGuard2026!",
        "role": "admin"
    },
    {
        "firstname": "Lead Risk",
        "lastname": "Analyst",
        "company": "RiskGuard Analytics",
        "email": "analyst@riskguard.internal",
        "password": "Analyst@RiskGuard2026!",
        "role": "user"
    }
]

DEMO_TASKS = [
    {
        "title": "Deploy FIDO2 Hardware MFA on All VPN Jump Hosts",
        "description": "Enforce physical YubiKey or authenticator MFA across all corporate access gateways.",
        "category": "Cybersecurity",
        "status": "In Progress",
        "owner": "Chief Information Security Officer (CISO)",
        "priority": "Critical",
        "due_date": "2026-11-15",
        "cost_estimate": "₹2.5 Lakhs",
        "treatment_type": "Reduce",
        "residual_risk": 150000.0
    },
    {
        "title": "Execute Invoice Factoring for Receivables > 45 Days",
        "description": "Partner with TReDS platform to accelerate working capital conversion cycle from 88 to 45 days.",
        "category": "Financial",
        "status": "Open",
        "owner": "Chief Financial Officer (CFO)",
        "priority": "High",
        "due_date": "2026-11-30",
        "cost_estimate": "₹1.2 Lakhs",
        "treatment_type": "Transfer",
        "residual_risk": 400000.0
    },
    {
        "title": "Pre-qualify Secondary Sourcing Vendors in South Corridor",
        "description": "Eliminate single-supplier concentration risk for critical raw material procurement.",
        "category": "Operations",
        "status": "Open",
        "owner": "Procurement Director",
        "priority": "High",
        "due_date": "2026-12-10",
        "cost_estimate": "₹80,000",
        "treatment_type": "Avoid",
        "residual_risk": 200000.0
    },
    {
        "title": "Establish Immutable Air-Gapped Database Backup Vault",
        "description": "Configure daily WORM-compliant snapshot replication to secondary cloud region with 4-hour RTO drills.",
        "category": "Cybersecurity",
        "status": "Closed",
        "owner": "Lead Infrastructure Architect",
        "priority": "Critical",
        "due_date": "2026-10-20",
        "cost_estimate": "₹1.8 Lakhs",
        "treatment_type": "Reduce",
        "residual_risk": 50000.0
    }
]


def seed():
    print("=" * 65)
    print("  RiskGuard Pro — Enterprise Demo Data Initialization")
    print("=" * 65)

    # 1. Initialize schema & default tables
    database.init_db()
    print("✓ Initialized database schema (SQLite + Supabase check).")

    # 2. Seed / ensure demo accounts
    print("\n--- [1/4] Seeding Demo User Accounts ---")
    for u in DEMO_USERS:
        existing = database.get_user_by_email(u["email"])
        if not existing:
            created = database.create_user(
                firstname=u["firstname"],
                lastname=u["lastname"],
                company=u["company"],
                email=u["email"],
                password=u["password"],
                role=u["role"]
            )
            uid = created.get("user", {}).get("id", "?")
            print(f"  + Created: {u['email']} [{u['role']}] (ID: {uid})")
        else:
            print(f"  * Exists:  {u['email']} [{existing['role']}] (ID: {existing['id']})")

    # 3. Seed sample assessment
    print("\n--- [2/4] Seeding Baseline Enterprise Risk Assessment ---")
    conn = database.get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM assessments")
    cnt = cur.fetchone()[0]
    if cnt == 0:
        sample_step_data = {
            "business": {
                "name": "Monte Carlo Retail Enterprises Ltd",
                "type": "Retail",
                "size": "Medium Enterprise",
                "location": "Mumbai, India",
                "employees": "250-500",
                "years": "14"
            },
            "financial": {
                "revenue": 24000000,
                "currentAssets": 6500000,
                "currentLiabilities": 4200000,
                "inventory": 2100000,
                "totalDebt": 5500000,
                "equity": 8500000,
                "netProfit": 1450000,
                "operatingProfit": 2600000,
                "cogs": 15000000,
                "interest": 350000,
                "avgReceivables": 1800000
            },
            "cyber": {
                "mfa_enabled": True,
                "backup_frequency": "daily",
                "vulnerability_score": 3.5
            }
        }
        database.save_assessment(
            user_id=1,
            company_name="Monte Carlo Retail Enterprises Ltd",
            industry="Retail",
            health_score=76,
            var_exposure=2880000.0,
            step_data=sample_step_data,
            ratios_data={"current_ratio": 1.55, "de_ratio": 0.65, "net_margin": 6.04}
        )
        print("  + Seeded baseline assessment for Monte Carlo Retail Enterprises Ltd.")
    else:
        print(f"  * Assessments already present ({cnt} records).")
    conn.close()

    # 4. Seed Action Tasks
    print("\n--- [3/4] Seeding ISO 31000 Action Tracker Tasks ---")
    cur_tasks = database.get_action_tasks()
    if len(cur_tasks) == 0:
        for t in DEMO_TASKS:
            created_t = database.create_action_task(t, user_id=1)
            print(f"  + Task #{created_t['id']}: {t['title'][:45]}... [{t['status']}]")
    else:
        print(f"  * Action tasks already present ({len(cur_tasks)} records).")

    # 5. Verify Hash Chain
    print("\n--- [4/4] Verifying Audit Trail Hash Chain ---")
    chain = database.verify_audit_chain()
    print(f"  ✓ Cryptographic Chain Integrity: {chain['valid']} ({chain['total_records']} verified records)")

    print("\n" + "=" * 65)
    print("  SEEDING COMPLETE — DEMO READY")
    print("=" * 65)
    print("  Admin Persona:   admin@riskguard.internal   / Admin@RiskGuard2026!")
    print("  Analyst Persona: analyst@riskguard.internal / Analyst@RiskGuard2026!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    seed()
