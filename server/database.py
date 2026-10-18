"""
Database Layer for RiskGuard Pro
Dual-Engine: Supabase (PostgreSQL Cloud) as primary with Local Fallback Resilience.
"""

import os
import sys
import sqlite3
from datetime import datetime, timezone
import random
from dotenv import load_dotenv

if sys.platform.startswith('win'):
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Try importing supabase
try:
    from supabase import create_client, Client
    HAS_SUPABASE_LIB = True
except ImportError:
    HAS_SUPABASE_LIB = False
    Client = None

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, '..', '.env')
LOCAL_DB_FILE = os.path.join(BASE_DIR, 'riskguard.db')

# Load environment variables
load_dotenv(ENV_FILE)

SUPABASE_URL = os.getenv('SUPABASE_URL', '').strip()
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '').strip()

_supabase_client = None
_using_supabase = False
_db_status_message = "Initializing database..."


# ─── Dual-Mode Engine Management ──────────────────────────────────────────────

def get_supabase_client():
    """Returns initialized Supabase client if valid credentials exist, else None."""
    global _supabase_client, SUPABASE_URL, SUPABASE_KEY
    if not HAS_SUPABASE_LIB:
        return None

    # Reload env in case it was updated
    load_dotenv(ENV_FILE, override=True)
    SUPABASE_URL = os.getenv('SUPABASE_URL', '').strip()
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '').strip()

    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    if 'your-project-id' in SUPABASE_URL or 'your-anon' in SUPABASE_KEY:
        return None

    try:
        if _supabase_client is None:
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _supabase_client
    except Exception as e:
        print(f"  ⚠️  Failed to create Supabase client: {e}")
        return None


def is_supabase_active():
    """Check if Supabase is currently active and reachable."""
    global _using_supabase
    return _using_supabase


def get_connection_status():
    """Retrieve detailed database connection status for dashboard UI telemetry."""
    global _using_supabase, _db_status_message, SUPABASE_URL

    masked_url = ""
    if SUPABASE_URL and 'your-project-id' not in SUPABASE_URL:
        # Mask project url e.g. https://ab*****.supabase.co
        try:
            parts = SUPABASE_URL.split('//')
            if len(parts) > 1:
                sub = parts[1].split('.')[0]
                masked_sub = sub[:3] + "****" if len(sub) > 3 else "****"
                masked_url = f"{parts[0]}//{masked_sub}.supabase.co"
            else:
                masked_url = SUPABASE_URL
        except Exception:
            masked_url = "https://****.supabase.co"

    has_creds = bool(SUPABASE_URL and SUPABASE_KEY and 'your-project-id' not in SUPABASE_URL)

    return {
        "is_supabase": _using_supabase,
        "provider": "Supabase Cloud (PostgreSQL)" if _using_supabase else "Local Engine (Safe Mode)",
        "configured": has_creds,
        "status": "connected" if _using_supabase else ("pending_setup" if has_creds else "placeholder_mode"),
        "supabase_url": masked_url,
        "message": _db_status_message,
        "library_installed": HAS_SUPABASE_LIB
    }


def init_db():
    """Initialize database: try Supabase first, fallback to SQLite if needed."""
    global _using_supabase, _db_status_message

    # Always ensure local SQLite schema is available for offline / fallback
    init_local_sqlite()

    client = get_supabase_client()
    if client:
        try:
            # Test query to check if 'risks' table exists in Supabase
            res = client.table('risks').select('id', count='exact').limit(1).execute()
            _using_supabase = True
            count = res.count if res.count is not None else len(res.data)
            _db_status_message = f"Connected to Supabase PostgreSQL ({count} risks in cloud)"
            print(f"  ☁️  {_db_status_message}")

            if count == 0:
                seed_supabase_data(client)
                print("  ✅ Seeded initial risk dataset into Supabase cloud.")
            return True
        except Exception as e:
            _using_supabase = False
            _db_status_message = f"Supabase connection warning: {str(e)}. Operating in Local Safe Mode."
            print(f"  ⚠️  {_db_status_message}")
            print("  ℹ️  Ensure you ran setup_supabase.sql in your Supabase SQL Editor.")
    else:
        _using_supabase = False
        _db_status_message = "Supabase credentials are placeholder in .env. Running on local database."
        print(f"  ℹ️  {_db_status_message}")

    return False


# ─── SQLite Local Fallback Engine ─────────────────────────────────────────────

def get_sqlite_conn():
    """Get connection to local SQLite database with Row dictionary factory."""
    conn = sqlite3.connect(LOCAL_DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_local_sqlite():
    """Create local SQLite tables if they do not exist and seed if empty."""
    conn = get_sqlite_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS risks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        category TEXT NOT NULL,
        likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
        impact INTEGER NOT NULL CHECK (impact BETWEEN 1 AND 5),
        score INTEGER NOT NULL,
        level TEXT NOT NULL,
        financial_impact REAL NOT NULL DEFAULT 0.0,
        owner TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active',
        velocity TEXT DEFAULT 'Medium',
        trend TEXT DEFAULT 'stable',
        mitigation TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        risk_id INTEGER,
        risk_name TEXT,
        action TEXT NOT NULL,
        details TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        source TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()

    # Check if empty, then seed
    cur.execute("SELECT COUNT(*) FROM risks")
    if cur.fetchone()[0] == 0:
        seed_local_sqlite(conn)
        print("  ✅ Seeded local database with enterprise risk dataset.")

    conn.close()


def calculate_level(score):
    """Calculate risk severity level based on 1-25 matrix scale."""
    if score >= 16:
        return "Critical"
    elif score >= 10:
        return "High"
    elif score >= 5:
        return "Medium"
    else:
        return "Low"


# ─── Seed Data ────────────────────────────────────────────────────────────────

ENTERPRISE_SEED_RISKS = [
    # Financial
    {
        "name": "Foreign Exchange Volatility",
        "description": "Unhedged currency fluctuations impacting international supply chain and cross-border settlement margins.",
        "category": "Financial", "likelihood": 4, "impact": 4, "score": 16, "level": "Critical",
        "financial_impact": 1850000.0, "owner": "CFO Office", "status": "Active",
        "velocity": "Fast", "trend": "increasing",
        "mitigation": "Implement rolling 90-day forward contracts and dynamic FX hedging corridors."
    },
    {
        "name": "Counterparty Credit Default",
        "description": "Key Tier-1 distribution partner showing liquidity distress, risking invoice settlement defaults.",
        "category": "Financial", "likelihood": 3, "impact": 4, "score": 12, "level": "High",
        "financial_impact": 950000.0, "owner": "Credit Committee", "status": "Mitigating",
        "velocity": "Medium", "trend": "stable",
        "mitigation": "Establish escrow payment milestones and mandate letters of credit for orders over $250k."
    },
    {
        "name": "Short-Term Liquidity Strain",
        "description": "Working capital gap during cyclical inventory pre-orders coinciding with quarterly tax liabilities.",
        "category": "Financial", "likelihood": 2, "impact": 5, "score": 10, "level": "High",
        "financial_impact": 1200000.0, "owner": "Treasury", "status": "Monitoring",
        "velocity": "Fast", "trend": "decreasing",
        "mitigation": "Secured $3.5M revolving credit facility with primary banking syndicate."
    },
    # Cybersecurity & Tech
    {
        "name": "Ransomware & Zero-Day Exploit",
        "description": "Advanced threat actor targeting core enterprise ERP and customer database backups.",
        "category": "Cybersecurity", "likelihood": 4, "impact": 5, "score": 20, "level": "Critical",
        "financial_impact": 3200000.0, "owner": "CISO Office", "status": "Active",
        "velocity": "Fast", "trend": "increasing",
        "mitigation": "Deploy air-gapped immutable backup vaults, EDR isolation agents, and 24/7 MDR SOC monitoring."
    },
    {
        "name": "Privileged Credential Compromise",
        "description": "Unauthorized credential harvesting through sophisticated spear-phishing targeting DevOps engineers.",
        "category": "Cybersecurity", "likelihood": 3, "impact": 4, "score": 12, "level": "High",
        "financial_impact": 780000.0, "owner": "SecOps Team", "status": "Mitigating",
        "velocity": "Fast", "trend": "decreasing",
        "mitigation": "Enforce hardware FIDO2 security keys, eliminate long-lived API tokens, and enforce PAM session recording."
    },
    {
        "name": "Cloud Infrastructure Outage",
        "description": "Multi-region availability zone blackout in primary cloud provider disrupting real-time order processing.",
        "category": "Cybersecurity", "likelihood": 2, "impact": 4, "score": 8, "level": "Medium",
        "financial_impact": 640000.0, "owner": "Infrastructure Lead", "status": "Monitoring",
        "velocity": "Medium", "trend": "stable",
        "mitigation": "Active-active multi-region failover cluster with automated DNS latency routing."
    },
    # Operational
    {
        "name": "Single-Source Semiconductor Shortage",
        "description": "Critical micro-controller component reliant on single manufacturing fab facing geopolitical export caps.",
        "category": "Operational", "likelihood": 4, "impact": 4, "score": 16, "level": "Critical",
        "financial_impact": 2400000.0, "owner": "Supply Chain VP", "status": "Active",
        "velocity": "Medium", "trend": "increasing",
        "mitigation": "Qualify secondary European supplier and maintain 6-month buffer stock in regional logistics hub."
    },
    {
        "name": "Core Warehouse Logistics Bottleneck",
        "description": "Automation crane failure and freight carrier capacity constraints causing fulfillment delivery delays.",
        "category": "Operational", "likelihood": 3, "impact": 3, "score": 9, "level": "Medium",
        "financial_impact": 420000.0, "owner": "Logistics Director", "status": "Mitigating",
        "velocity": "Slow", "trend": "decreasing",
        "mitigation": "Signed standby carrier SLA and deployed preventive IoT vibration sensors on crane motors."
    },
    {
        "name": "Key Executive Leadership Turnover",
        "description": "Sudden departure of Chief Technology Officer and Principal Systems Architect without designated successor.",
        "category": "Operational", "likelihood": 2, "impact": 3, "score": 6, "level": "Medium",
        "financial_impact": 350000.0, "owner": "HR / Executive Board", "status": "Monitoring",
        "velocity": "Slow", "trend": "stable",
        "mitigation": "Executive retention bonus package and comprehensive knowledge transfer program."
    },
    # Compliance & Regulatory
    {
        "name": "Cross-Border Data Privacy Non-Compliance",
        "description": "New stringent AI governance and GDPR Article 28 data processor auditing requirements with punitive penalties.",
        "category": "Compliance", "likelihood": 3, "impact": 4, "score": 12, "level": "High",
        "financial_impact": 1500000.0, "owner": "Chief Legal Officer", "status": "Active",
        "velocity": "Slow", "trend": "increasing",
        "mitigation": "Retain external privacy counsel for biannual audits; integrate automated data lineage mapping."
    },
    {
        "name": "ESG Carbon Disclosure Sanctions",
        "description": "Failure to meet mandatory Scope 3 emissions reporting timeline for institutional European investors.",
        "category": "Compliance", "likelihood": 2, "impact": 3, "score": 6, "level": "Medium",
        "financial_impact": 300000.0, "owner": "Sustainability Officer", "status": "Monitoring",
        "velocity": "Slow", "trend": "stable",
        "mitigation": "Integrated automated carbon accounting software connected directly to logistics ERP."
    },
    # Strategic
    {
        "name": "Disruptive Generative AI Competitor",
        "description": "Agile startup launching competitive automated risk analytics suite at 60% lower subscription tier.",
        "category": "Strategic", "likelihood": 4, "impact": 3, "score": 12, "level": "High",
        "financial_impact": 1100000.0, "owner": "Chief Strategy Officer", "status": "Active",
        "velocity": "Fast", "trend": "increasing",
        "mitigation": "Accelerate native proprietary ML features and bundle predictive workflow automations."
    },
    {
        "name": "Negative PR & Brand Sentiment Spillover",
        "description": "Social media misinformation campaign regarding product sustainability claims.",
        "category": "Strategic", "likelihood": 2, "impact": 4, "score": 8, "level": "Medium",
        "financial_impact": 500000.0, "owner": "Corporate Communications", "status": "Monitoring",
        "velocity": "Fast", "trend": "decreasing",
        "mitigation": "Engaged dedicated crisis communications agency and 24/7 brand sentiment listening dashboard."
    }
]

ENTERPRISE_SEED_ALERTS = [
    {"type": "critical", "source": "Cybersecurity", "message": "Zero-day exploit detected in perimeter gateway. Urgent patching mandated.", "is_read": 0},
    {"type": "critical", "source": "Financial", "message": "Foreign exchange exposure breached 15% threshold against EUR/USD pair.", "is_read": 0},
    {"type": "warning", "source": "Supply Chain", "message": "Taiwan component supplier confirmed 4-week lead time extension.", "is_read": 0},
    {"type": "info", "source": "Compliance", "message": "Q4 ISO 27001 compliance surveillance audit successfully initiated.", "is_read": 1},
    {"type": "warning", "source": "Financial", "message": "Counterparty credit review flagged delayed payment on account #9042.", "is_read": 0}
]


def seed_local_sqlite(conn):
    """Seed SQLite database."""
    cur = conn.cursor()
    for r in ENTERPRISE_SEED_RISKS:
        cur.execute("""
            INSERT INTO risks (name, description, category, likelihood, impact, score, level,
                               financial_impact, owner, status, velocity, trend, mitigation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["name"], r["description"], r["category"], r["likelihood"], r["impact"],
            r["score"], r["level"], r["financial_impact"], r["owner"], r["status"],
            r["velocity"], r["trend"], r["mitigation"]
        ))
        risk_id = cur.lastrowid
        cur.execute("""
            INSERT INTO audit_logs (risk_id, risk_name, action, details)
            VALUES (?, ?, 'CREATED', 'Initial risk registration and baseline impact assessment.')
        """, (risk_id, r["name"]))

    for a in ENTERPRISE_SEED_ALERTS:
        cur.execute("""
            INSERT INTO alerts (type, source, message, is_read)
            VALUES (?, ?, ?, ?)
        """, (a["type"], a["source"], a["message"], a["is_read"]))
    conn.commit()


def seed_supabase_data(client):
    """Seed Supabase cloud tables."""
    client.table('risks').insert(ENTERPRISE_SEED_RISKS).execute()
    result = client.table('risks').select('id, name').execute()
    inserted_risks = result.data or []

    audit_logs = []
    for risk in inserted_risks:
        audit_logs.append({
            "risk_id": risk["id"],
            "risk_name": risk["name"],
            "action": "CREATED",
            "details": "Initial risk registration and baseline impact assessment."
        })
    if audit_logs:
        client.table('audit_logs').insert(audit_logs).execute()

    supabase_alerts = [
        {"type": a["type"], "source": a["source"], "message": a["message"], "is_read": bool(a["is_read"])}
        for a in ENTERPRISE_SEED_ALERTS
    ]
    client.table('alerts').insert(supabase_alerts).execute()


# ─── CRUD Operations (Unified for Supabase & SQLite) ─────────────────────────

def get_all_risks(category=None, level=None, status=None, search=None):
    """Retrieve risks with dynamic filtering from active engine."""
    client = get_supabase_client() if _using_supabase else None

    if client:
        try:
            query = client.table('risks').select('*')
            if category and category != "All":
                query = query.eq('category', category)
            if level and level != "All":
                query = query.eq('level', level)
            if status and status != "All":
                query = query.eq('status', status)
            if search:
                query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%,owner.ilike.%{search}%")

            query = query.order('score', desc=True).order('financial_impact', desc=True)
            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"  ⚠️  Supabase query error: {e}, falling back to local DB")

    # Local SQLite Fallback
    conn = get_sqlite_conn()
    cur = conn.cursor()
    query = "SELECT * FROM risks WHERE 1=1"
    params = []

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if level and level != "All":
        query += " AND level = ?"
        params.append(level)
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)
    if search:
        query += " AND (name LIKE ? OR description LIKE ? OR owner LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])

    query += " ORDER BY score DESC, financial_impact DESC"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_risk_by_id(risk_id):
    """Retrieve a single risk by primary ID."""
    client = get_supabase_client() if _using_supabase else None

    if client:
        try:
            res = client.table('risks').select('*').eq('id', risk_id).limit(1).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"  ⚠️  Supabase get error: {e}")

    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM risks WHERE id = ?", (risk_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def create_risk(data):
    """Insert a new risk and record an audit log entry."""
    likelihood = int(data.get("likelihood", 3))
    impact = int(data.get("impact", 3))
    score = likelihood * impact
    level = calculate_level(score)
    fin = float(data.get("financial_impact", 0.0))

    risk_data = {
        "name": data.get("name", "Untitled Risk"),
        "description": data.get("description", ""),
        "category": data.get("category", "Operational"),
        "likelihood": likelihood,
        "impact": impact,
        "score": score,
        "level": level,
        "financial_impact": fin,
        "owner": data.get("owner", "Risk Management"),
        "status": data.get("status", "Active"),
        "velocity": data.get("velocity", "Medium"),
        "trend": data.get("trend", "stable"),
        "mitigation": data.get("mitigation", "")
    }

    client = get_supabase_client() if _using_supabase else None
    if client:
        try:
            res = client.table('risks').insert(risk_data).execute()
            new_risk = res.data[0] if res.data else None
            if new_risk:
                client.table('audit_logs').insert({
                    "risk_id": new_risk["id"],
                    "risk_name": new_risk["name"],
                    "action": "CREATED",
                    "details": f"New risk added with score {score}/25 ({level}) and exposure ${fin:,.2f}"
                }).execute()

                if level == "Critical":
                    client.table('alerts').insert({
                        "type": "critical",
                        "source": data.get("category", "Operational"),
                        "message": f"High-severity critical risk registered: '{data.get('name')}'",
                        "is_read": False
                    }).execute()
                return new_risk
        except Exception as e:
            print(f"  ⚠️  Supabase insert error: {e}")

    # Local SQLite
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO risks (name, description, category, likelihood, impact, score, level,
                           financial_impact, owner, status, velocity, trend, mitigation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        risk_data["name"], risk_data["description"], risk_data["category"],
        risk_data["likelihood"], risk_data["impact"], risk_data["score"],
        risk_data["level"], risk_data["financial_impact"], risk_data["owner"],
        risk_data["status"], risk_data["velocity"], risk_data["trend"], risk_data["mitigation"]
    ))
    new_id = cur.lastrowid

    cur.execute("""
        INSERT INTO audit_logs (risk_id, risk_name, action, details)
        VALUES (?, ?, 'CREATED', ?)
    """, (new_id, risk_data["name"], f"New risk added with score {score}/25 ({level}) and exposure ${fin:,.2f}"))

    if level == "Critical":
        cur.execute("""
            INSERT INTO alerts (type, source, message, is_read)
            VALUES ('critical', ?, ?, 0)
        """, (risk_data["category"], f"High-severity critical risk registered: '{risk_data['name']}'"))

    conn.commit()
    cur.execute("SELECT * FROM risks WHERE id = ?", (new_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_risk(risk_id, data):
    """Update an existing risk, recalculate score, and record audit trail."""
    existing = get_risk_by_id(risk_id)
    if not existing:
        return None

    likelihood = int(data.get("likelihood", existing["likelihood"]))
    impact = int(data.get("impact", existing["impact"]))
    score = likelihood * impact
    level = calculate_level(score)

    update_data = {
        "name": data.get("name", existing["name"]),
        "description": data.get("description", existing["description"]),
        "category": data.get("category", existing["category"]),
        "likelihood": likelihood,
        "impact": impact,
        "score": score,
        "level": level,
        "financial_impact": float(data.get("financial_impact", existing["financial_impact"])),
        "owner": data.get("owner", existing["owner"]),
        "status": data.get("status", existing["status"]),
        "velocity": data.get("velocity", existing["velocity"]),
        "trend": data.get("trend", existing["trend"]),
        "mitigation": data.get("mitigation", existing["mitigation"])
    }

    changes = []
    if existing.get("status") != update_data["status"]:
        changes.append(f"Status changed from {existing.get('status')} to {update_data['status']}")
    if existing.get("score") != score:
        changes.append(f"Score updated from {existing.get('score')} to {score} ({level})")
    if not changes:
        changes.append("General risk details and mitigation plan updated.")
    change_summary = "; ".join(changes)

    client = get_supabase_client() if _using_supabase else None
    if client:
        try:
            client.table('risks').update(update_data).eq('id', risk_id).execute()
            client.table('audit_logs').insert({
                "risk_id": risk_id,
                "risk_name": update_data["name"],
                "action": "UPDATED",
                "details": change_summary
            }).execute()
            return get_risk_by_id(risk_id)
        except Exception as e:
            print(f"  ⚠️  Supabase update error: {e}")

    # Local SQLite
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE risks SET name=?, description=?, category=?, likelihood=?, impact=?,
                         score=?, level=?, financial_impact=?, owner=?, status=?,
                         velocity=?, trend=?, mitigation=?, updated_at=CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        update_data["name"], update_data["description"], update_data["category"],
        update_data["likelihood"], update_data["impact"], update_data["score"],
        update_data["level"], update_data["financial_impact"], update_data["owner"],
        update_data["status"], update_data["velocity"], update_data["trend"],
        update_data["mitigation"], risk_id
    ))
    cur.execute("""
        INSERT INTO audit_logs (risk_id, risk_name, action, details)
        VALUES (?, ?, 'UPDATED', ?)
    """, (risk_id, update_data["name"], change_summary))
    conn.commit()
    conn.close()
    return get_risk_by_id(risk_id)


def delete_risk(risk_id):
    """Delete a risk from database."""
    existing = get_risk_by_id(risk_id)
    if not existing:
        return False

    client = get_supabase_client() if _using_supabase else None
    if client:
        try:
            client.table('risks').delete().eq('id', risk_id).execute()
            client.table('audit_logs').insert({
                "risk_id": risk_id,
                "risk_name": existing["name"],
                "action": "DELETED",
                "details": f"Risk removed from enterprise registry (Previous score: {existing['score']})"
            }).execute()
            return True
        except Exception as e:
            print(f"  ⚠️  Supabase delete error: {e}")

    # Local SQLite
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM risks WHERE id = ?", (risk_id,))
    cur.execute("""
        INSERT INTO audit_logs (risk_id, risk_name, action, details)
        VALUES (?, ?, 'DELETED', ?)
    """, (risk_id, existing["name"], f"Risk removed from enterprise registry (Previous score: {existing['score']})"))
    conn.commit()
    conn.close()
    return True


# ─── Analytics, Matrix & Telemetry ───────────────────────────────────────────

def get_dashboard_stats():
    """Calculate executive KPI summary."""
    all_risks = get_all_risks()
    total_risks = len(all_risks)
    active_risks_list = [r for r in all_risks if r.get('status') != 'Closed']
    active_risks = len(active_risks_list)

    critical_count = sum(1 for r in active_risks_list if r.get('level') == 'Critical')
    high_count = sum(1 for r in active_risks_list if r.get('level') == 'High')
    medium_count = sum(1 for r in active_risks_list if r.get('level') == 'Medium')
    low_count = sum(1 for r in active_risks_list if r.get('level') == 'Low')

    total_financial_var = sum(float(r.get('financial_impact') or 0.0) for r in active_risks_list)
    avg_score = round(sum(int(r.get('score') or 0) for r in active_risks_list) / max(active_risks, 1), 1)

    categories_map = {}
    for r in active_risks_list:
        cat = r.get('category', 'Other')
        if cat not in categories_map:
            categories_map[cat] = {
                "category": cat, "count": 0, "total_financial": 0.0,
                "avg_score": 0.0, "critical_count": 0, "_scores": []
            }
        categories_map[cat]["count"] += 1
        categories_map[cat]["total_financial"] += float(r.get('financial_impact') or 0.0)
        categories_map[cat]["_scores"].append(int(r.get('score') or 0))
        if r.get('level') == 'Critical':
            categories_map[cat]["critical_count"] += 1

    categories = []
    for cat_data in categories_map.values():
        cat_data["avg_score"] = round(sum(cat_data["_scores"]) / max(len(cat_data["_scores"]), 1), 1)
        del cat_data["_scores"]
        categories.append(cat_data)
    categories.sort(key=lambda x: x["total_financial"], reverse=True)

    # Unread alerts
    unread_alerts = 0
    client = get_supabase_client() if _using_supabase else None
    if client:
        try:
            ar = client.table('alerts').select('id', count='exact').eq('is_read', False).execute()
            unread_alerts = ar.count if ar.count is not None else len(ar.data)
        except Exception:
            unread_alerts = 2
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM alerts WHERE is_read = 0")
        unread_alerts = cur.fetchone()[0]
        conn.close()

    # Health score
    health_penalty = (critical_count * 12) + (high_count * 6) + (medium_count * 2)
    health_score = max(10, min(100, 100 - health_penalty))

    return {
        "totalRisks": total_risks,
        "activeRisks": active_risks,
        "criticalCount": critical_count,
        "highCount": high_count,
        "mediumCount": medium_count,
        "lowCount": low_count,
        "totalFinancialVaR": total_financial_var,
        "avgScore": avg_score,
        "healthScore": health_score,
        "categories": categories,
        "unreadAlerts": unread_alerts,
        "db_info": get_connection_status()
    }


def get_matrix_data():
    """Group risks by Likelihood (1-5) and Impact (1-5) for 5x5 Matrix."""
    risks = [r for r in get_all_risks() if r.get('status') != 'Closed']

    matrix_cells = {}
    for l in range(1, 6):
        for i in range(1, 6):
            matrix_cells[f"{l}_{i}"] = {
                "likelihood": l,
                "impact": i,
                "score": l * i,
                "level": calculate_level(l * i),
                "count": 0,
                "risks": []
            }

    for r in risks:
        key = f"{r.get('likelihood')}_{r.get('impact')}"
        if key in matrix_cells:
            matrix_cells[key]["count"] += 1
            matrix_cells[key]["risks"].append(r)

    return list(matrix_cells.values())


def get_audit_logs(limit=30):
    """Get recent audit activity trail."""
    client = get_supabase_client() if _using_supabase else None
    if client:
        try:
            res = client.table('audit_logs').select('*').order('created_at', desc=True).limit(limit).execute()
            return res.data or []
        except Exception as e:
            print(f"  ⚠️  Supabase audit log query error: {e}")

    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_alerts():
    """Get alerts list."""
    client = get_supabase_client() if _using_supabase else None
    if client:
        try:
            res = client.table('alerts').select('*').order('created_at', desc=True).limit(30).execute()
            return res.data or []
        except Exception as e:
            print(f"  ⚠️  Supabase alerts query error: {e}")

    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 30")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def mark_alert_read(alert_id):
    """Mark alert as read."""
    client = get_supabase_client() if _using_supabase else None
    if client:
        try:
            client.table('alerts').update({"is_read": True}).eq('id', alert_id).execute()
            return True
        except Exception as e:
            print(f"  ⚠️  Supabase alert update error: {e}")

    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("UPDATE alerts SET is_read = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    return True


def reset_seed_data():
    """Reset database to initial enterprise demo dataset."""
    client = get_supabase_client() if _using_supabase else None
    if client:
        try:
            client.table('risks').delete().neq('id', 0).execute()
            client.table('audit_logs').delete().neq('id', 0).execute()
            client.table('alerts').delete().neq('id', 0).execute()
            seed_supabase_data(client)
            return True
        except Exception as e:
            print(f"  ⚠️  Supabase reset seed error: {e}")

    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM risks")
    cur.execute("DELETE FROM audit_logs")
    cur.execute("DELETE FROM alerts")
    conn.commit()
    seed_local_sqlite(conn)
    conn.close()
    return True


# ─── Supabase Configuration & Sync Endpoint Handlers ──────────────────────────

def configure_supabase_credentials(new_url, new_key, sync_data=True):
    """Update .env with new Supabase credentials and attempt connection & data sync."""
    global _supabase_client, _using_supabase, _db_status_message, SUPABASE_URL, SUPABASE_KEY

    new_url = new_url.strip()
    new_key = new_key.strip()

    if not new_url or not new_key:
        return {"success": False, "error": "Both Supabase URL and Key are required."}

    # Test creating client and making query
    try:
        test_client = create_client(new_url, new_key)
        res = test_client.table('risks').select('id', count='exact').limit(1).execute()
        count = res.count if res.count is not None else len(res.data)
    except Exception as e:
        err = str(e)
        if "relation \"risks\" does not exist" in err.lower() or "404" in err:
            return {
                "success": False,
                "error": "Connected to Supabase, but the 'risks' table was not found! Please run setup_supabase.sql in your Supabase SQL Editor first."
            }
        return {"success": False, "error": f"Failed to connect to Supabase: {err}"}

    # Connection succeeded! Write to .env
    try:
        env_content = f"# RiskGuard Pro -- Supabase Configuration\nSUPABASE_URL={new_url}\nSUPABASE_KEY={new_key}\n"
        with open(ENV_FILE, 'w', encoding='utf-8') as f:
            f.write(env_content)
    except Exception as e:
        print(f"  ⚠️  Warning saving .env file: {e}")

    # Switch active client
    _supabase_client = test_client
    _using_supabase = True
    SUPABASE_URL = new_url
    SUPABASE_KEY = new_key
    _db_status_message = f"Connected to Supabase Cloud PostgreSQL ({count} risks)"

    # Seed if cloud empty
    if count == 0 and sync_data:
        local_risks = get_all_risks()
        if local_risks:
            # Insert existing local risks into Supabase
            clean_risks = []
            for r in local_risks:
                clean_risks.append({
                    "name": r["name"], "description": r.get("description", ""),
                    "category": r["category"], "likelihood": r["likelihood"],
                    "impact": r["impact"], "score": r["score"], "level": r["level"],
                    "financial_impact": float(r.get("financial_impact", 0)),
                    "owner": r["owner"], "status": r.get("status", "Active"),
                    "velocity": r.get("velocity", "Medium"), "trend": r.get("trend", "stable"),
                    "mitigation": r.get("mitigation", "")
                })
            test_client.table('risks').insert(clean_risks).execute()
        else:
            seed_supabase_data(test_client)

    return {
        "success": True,
        "message": "Successfully connected to Supabase Cloud Database!",
        "status": get_connection_status()
    }
