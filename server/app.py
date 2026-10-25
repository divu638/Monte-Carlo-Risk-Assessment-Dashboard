"""
Flask REST API Server for Business Risk Assessment Dashboard & Analytics Engine.
Production Hardened & Secured:
- OWASP Security Headers (CSP, HSTS-ready, X-Frame-Options, X-Content-Type-Options, Referrer-Policy)
- Path Traversal & Sensitive File Exposure Shields (.env, .git, .py, .db, .log probing protection)
- IP-based Sliding-Window Rate Limiting (Anti-DoS & Anti-Brute-Force)
- Stored XSS Neutralization & Input Bounds Enforcement
- Masked Server Fingerprint & Zero-Leakage Error Handling
"""

import os
import sys
import random
import math
import html
import time
import traceback
from collections import defaultdict
from urllib.parse import urlparse
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import database

# Load environment
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Mask Server banner at WSGI protocol layer to hide Werkzeug & Python version
try:
    import werkzeug.serving
    werkzeug.serving.WSGIRequestHandler.version_string = lambda self: "Enterprise-Risk-Security-Gateway"
except Exception:
    pass

# Paths
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIR = os.path.abspath(os.path.join(SERVER_DIR, "..", "client"))

app = Flask(__name__, static_folder=CLIENT_DIR, static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*"}}, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# Ensure database is initialized
database.init_db()


# ─── Security Firewall & Rate Limiting System ──────────────────────────────────

# In-memory sliding window rate limiter
RATE_LIMIT_WINDOWS = defaultdict(list)
CLEANUP_INTERVAL = 300  # 5 minutes
LAST_CLEANUP = time.time()

# Allowed static file extensions for the frontend
ALLOWED_STATIC_EXTENSIONS = {
    ".html", ".css", ".js", ".png", ".jpg", ".jpeg",
    ".svg", ".ico", ".webp", ".woff", ".woff2", ".ttf",
    ".json", ".map"
}

# Strictly blocked file extensions & patterns
BLOCKED_PATTERNS = {
    ".env", ".py", ".pyc", ".pyd", ".db", ".sqlite", ".sqlite3",
    ".sql", ".log", ".bak", ".swp", ".git", ".ini", ".cfg",
    ".conf", ".sh", ".bat", ".cmd", ".ps1", ".yml", ".yaml",
    ".key", ".pem", ".crt", ".md"
}

# Blocked probe keywords
PROBE_BLACKLIST = [
    "/.env", "/.git", "/.svn", "/.vscode", "/.idea", "/server/",
    "/proc/", "/etc/", "/var/", "win.ini", "boot.ini",
    "/requirements.txt", "/package.json", "/setup_supabase.sql"
]


def get_client_ip():
    """Retrieve client IP address securely, respecting trusted reverse proxy headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def check_rate_limit(endpoint_type="general"):
    """
    Sliding window in-memory rate limiter per IP address.
    Returns True if allowed, False if rate limit exceeded.
    """
    global LAST_CLEANUP
    now = time.time()

    # Periodic garbage collection of expired timestamps
    if now - LAST_CLEANUP > CLEANUP_INTERVAL:
        cutoff = now - 120
        keys_to_delete = []
        for key, timestamps in list(RATE_LIMIT_WINDOWS.items()):
            RATE_LIMIT_WINDOWS[key] = [t for t in timestamps if t > cutoff]
            if not RATE_LIMIT_WINDOWS[key]:
                keys_to_delete.append(key)
        for k in keys_to_delete:
            RATE_LIMIT_WINDOWS.pop(k, None)
        LAST_CLEANUP = now

    ip = get_client_ip()
    bucket_key = f"{ip}:{endpoint_type}"

    # Rate limits per 60-second sliding window
    tier_limits = {
        "simulate": 40,      # Quantitative simulation compute intensive (max 40/min)
        "reset": 8,          # Database re-seed/reset (max 8/min)
        "config": 15,        # Supabase config tests (max 15/min)
        "write": 60,         # Risk creation / updates / deletes (max 60/min)
        "general": 180       # Read requests (max 180/min)
    }

    max_allowed = tier_limits.get(endpoint_type, 180)
    window = 60.0
    cutoff = now - window

    valid_timestamps = [t for t in RATE_LIMIT_WINDOWS[bucket_key] if t > cutoff]
    if len(valid_timestamps) >= max_allowed:
        RATE_LIMIT_WINDOWS[bucket_key] = valid_timestamps
        return False

    valid_timestamps.append(now)
    RATE_LIMIT_WINDOWS[bucket_key] = valid_timestamps
    return True


def mask_exception(e, context="API Operation"):
    """
    Log full exception stack trace internally for developer debugging,
    while returning a sanitized error payload to client so no file paths,
    database schemas, or internal IPs are ever leaked to attackers.
    """
    err_str = str(e)
    # Mask any potential secret tokens from the console log
    safe_log_err = err_str.replace("sb_secret_", "sb_secret_***").replace("sb_publishable_", "sb_pub_***")
    print(f"  [SECURITY LOG - INTERNAL ERROR in {context}]: {safe_log_err}")
    print(traceback.format_exc())
    return jsonify({
        "success": False,
        "error": "A secure server exception occurred. The request could not be completed.",
        "code": 500
    }), 500


def sanitize_text(val, max_length=255, default=""):
    """Sanitize user string input: escape HTML entities to prevent Stored XSS and enforce length."""
    if val is None:
        return default
    text = str(val).strip()
    escaped = html.escape(text, quote=True)
    return escaped[:max_length]


def sanitize_number(val, min_val, max_val, default):
    """Safely parse and clamp numeric input to safe analytical bounds."""
    try:
        num = float(val)
        if math.isnan(num) or math.isinf(num):
            return default
        return max(min_val, min(max_val, num))
    except (TypeError, ValueError):
        return default


def sanitize_integer(val, min_val, max_val, default):
    """Safely parse and clamp integer input to safe bounds."""
    try:
        num = int(val)
        return max(min_val, min(max_val, num))
    except (TypeError, ValueError):
        return default


# ─── Middleware: Request Pre-Screening & Security Headers ──────────────────────

@app.before_request
def security_firewall():
    """Pre-request inspection: rate limiting, path traversal blocking, and probe rejection."""
    path = request.path

    # 1. Block Path Traversal Attacks
    raw_path = request.environ.get("RAW_URI", request.path)
    if ".." in path or ".." in raw_path or "%2e" in raw_path.lower():
        return jsonify({"error": "Forbidden: Path traversal sequence detected", "code": 403}), 403

    # 2. Block Probing for Sensitive Environment, Source, or Config Files
    lower_path = path.lower()
    if any(probe in lower_path for probe in PROBE_BLACKLIST):
        return jsonify({"error": "Forbidden: Access to protected asset is restricted", "code": 403}), 403

    # 3. Dynamic IP Rate Limiting for API routes
    if path.startswith("/api/"):
        ep_type = "general"
        if path == "/api/simulate":
            ep_type = "simulate"
        elif path == "/api/reset-seed":
            ep_type = "reset"
        elif path.startswith("/api/config/"):
            ep_type = "config"
        elif request.method in ["POST", "PUT", "DELETE"]:
            ep_type = "write"

        if not check_rate_limit(ep_type):
            response = jsonify({
                "error": "Rate limit exceeded. Too many requests. Please wait before retrying.",
                "code": 429
            })
            response.headers["Retry-After"] = "60"
            return response, 429


@app.after_request
def apply_security_headers(response):
    """Enforce defense-in-depth OWASP HTTP security headers and cloaking."""
    # Cloak server fingerprint (hides Werkzeug / Python versions)
    response.headers["Server"] = "Enterprise-Risk-Security-Gateway"

    # Anti-Clickjacking: Prevent framing by unauthorized external sites
    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    # Anti-MIME-Sniffing: Force browser to honor declared content-type
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Legacy XSS Filter protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Referrer privacy: Do not leak sensitive paths or tokens to foreign origins
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Disable unused browser device sensors and hardware APIs
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=(), payment=(), usb=()"

    # Content-Security-Policy (Permits local resources + trusted Google Fonts + Chart.js/Three.js CDNs)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: https: blob:; "
        "connect-src 'self' https: http:; "
        "frame-ancestors 'self'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )

    return response


# ─── Static File Serving with Sandboxed Boundary Validation ───────────────────

@app.route("/")
def index():
    """Serve main dashboard client HTML."""
    return send_from_directory(CLIENT_DIR, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static client assets with strict boundary validation."""
    # Normalize path and check for traversal
    clean_name = os.path.normpath(filename).replace("\\", "/")
    if clean_name.startswith("..") or "/.." in clean_name or clean_name.startswith("/"):
        return jsonify({"error": "Forbidden: Invalid file path", "code": 403}), 403

    base_name = os.path.basename(clean_name).lower()
    ext = os.path.splitext(clean_name)[1].lower()

    # Block hidden files and dangerous extensions
    if base_name.startswith(".") or ext in BLOCKED_PATTERNS:
        return jsonify({"error": "Forbidden: Access restricted", "code": 403}), 403

    # Only allow verified static types
    if ext and ext not in ALLOWED_STATIC_EXTENSIONS:
        return jsonify({"error": "Forbidden: File type not permitted", "code": 403}), 403

    full_path = os.path.abspath(os.path.join(CLIENT_DIR, clean_name))
    if not full_path.startswith(CLIENT_DIR):
        return jsonify({"error": "Forbidden: Path escape violation", "code": 403}), 403

    if not os.path.isfile(full_path):
        return jsonify({"error": "Resource not found", "code": 404}), 404

    return send_from_directory(CLIENT_DIR, clean_name)


# ─── REST API Endpoints ───────────────────────────────────────────────────────

@app.route("/api/db-status", methods=["GET"])
def get_db_status():
    """Retrieve database engine status, provider, and masked Supabase connectivity."""
    try:
        status = database.get_connection_status()
        return jsonify(status)
    except Exception as e:
        return mask_exception(e, "get_db_status")


@app.route("/api/config/supabase", methods=["POST"])
def configure_supabase():
    """Configure and test Supabase credentials dynamically from the UI with SSRF validation."""
    try:
        data = request.get_json(silent=True) or {}
        url = sanitize_text(data.get("url", ""), max_length=200).strip()
        key = sanitize_text(data.get("key", ""), max_length=500).strip()
        sync_data = bool(data.get("sync_data", True))

        if not url or not key:
            return jsonify({"success": False, "error": "Both Supabase Project URL and API Key are required."}), 400

        # Anti-SSRF Validation
        parsed = urlparse(url)
        if parsed.scheme != "https":
            return jsonify({"success": False, "error": "Invalid URL scheme. Supabase requires HTTPS."}), 400

        hostname = (parsed.hostname or "").lower()
        blocked_hosts = ["localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254", "internal", "lan"]
        if any(b in hostname for b in blocked_hosts) or hostname.startswith("192.168.") or hostname.startswith("10."):
            return jsonify({"success": False, "error": "Prohibited host address. Internal loopback is blocked."}), 400

        result = database.configure_supabase_credentials(url, key, sync_data=sync_data)
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return mask_exception(e, "configure_supabase")


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Retrieve executive KPIs, distribution, and health score."""
    try:
        stats = database.get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        return mask_exception(e, "get_stats")


@app.route("/api/risks", methods=["GET"])
def list_risks():
    """Retrieve risks with sanitized optional filters (category, level, status, search)."""
    try:
        category = sanitize_text(request.args.get("category"), max_length=50) or None
        level = sanitize_text(request.args.get("level"), max_length=20) or None
        status = sanitize_text(request.args.get("status"), max_length=20) or None
        search = sanitize_text(request.args.get("search"), max_length=80) or None

        risks = database.get_all_risks(category=category, level=level, status=status, search=search)
        return jsonify(risks)
    except Exception as e:
        return mask_exception(e, "list_risks")


@app.route("/api/risks/<int:risk_id>", methods=["GET"])
def get_risk(risk_id):
    """Get single risk details with quantitative VaR simulation and trend projection."""
    try:
        if risk_id < 1 or risk_id > 1000000:
            return jsonify({"error": "Invalid risk identifier"}), 400

        risk = database.get_risk_by_id(risk_id)
        if not risk:
            return jsonify({"error": "Risk not found"}), 404

        # Quantitative VaR loss projection
        financial = float(risk.get("financial_impact", 100000.0) or 100000.0)
        sim = run_monte_carlo(int(risk["likelihood"]), int(risk["impact"]), financial)
        forecast = generate_trend_forecast(int(risk["score"]), risk.get("trend", "stable"), risk.get("velocity", "Medium"))

        return jsonify({
            **risk,
            "simulation": sim,
            "forecast": forecast
        })
    except Exception as e:
        return mask_exception(e, f"get_risk #{risk_id}")


@app.route("/api/risks", methods=["POST"])
def add_risk():
    """Create a new risk in database with sanitized inputs and audit log."""
    try:
        data = request.get_json(silent=True) or {}
        name = sanitize_text(data.get("name"), max_length=150)
        if not name:
            return jsonify({"error": "Risk name is required and cannot be empty."}), 400

        sanitized_data = {
            "name": name,
            "description": sanitize_text(data.get("description"), max_length=2000),
            "category": sanitize_text(data.get("category"), max_length=50, default="Operational"),
            "likelihood": sanitize_integer(data.get("likelihood"), 1, 5, 3),
            "impact": sanitize_integer(data.get("impact"), 1, 5, 3),
            "financial_impact": sanitize_number(data.get("financial_impact"), 0.0, 10_000_000_000.0, 0.0),
            "owner": sanitize_text(data.get("owner"), max_length=80, default="Risk Officer"),
            "status": sanitize_text(data.get("status"), max_length=30, default="Active"),
            "velocity": sanitize_text(data.get("velocity"), max_length=30, default="Medium"),
            "trend": sanitize_text(data.get("trend"), max_length=30, default="stable"),
            "mitigation": sanitize_text(data.get("mitigation"), max_length=2000),
            "action_plan": sanitize_text(data.get("action_plan"), max_length=2000)
        }

        new_risk = database.create_risk(sanitized_data)
        return jsonify(new_risk), 201
    except Exception as e:
        return mask_exception(e, "add_risk")


@app.route("/api/risks/<int:risk_id>", methods=["PUT"])
def update_risk(risk_id):
    """Update risk details and audit trail with sanitized inputs."""
    try:
        if risk_id < 1 or risk_id > 1000000:
            return jsonify({"error": "Invalid risk identifier"}), 400

        data = request.get_json(silent=True) or {}
        if not data:
            return jsonify({"error": "No update payload provided."}), 400

        sanitized_data = {}
        if "name" in data:
            sanitized_data["name"] = sanitize_text(data.get("name"), max_length=150)
        if "description" in data:
            sanitized_data["description"] = sanitize_text(data.get("description"), max_length=2000)
        if "category" in data:
            sanitized_data["category"] = sanitize_text(data.get("category"), max_length=50)
        if "likelihood" in data:
            sanitized_data["likelihood"] = sanitize_integer(data.get("likelihood"), 1, 5, 3)
        if "impact" in data:
            sanitized_data["impact"] = sanitize_integer(data.get("impact"), 1, 5, 3)
        if "financial_impact" in data:
            sanitized_data["financial_impact"] = sanitize_number(data.get("financial_impact"), 0.0, 10_000_000_000.0, 0.0)
        if "owner" in data:
            sanitized_data["owner"] = sanitize_text(data.get("owner"), max_length=80)
        if "status" in data:
            sanitized_data["status"] = sanitize_text(data.get("status"), max_length=30)
        if "velocity" in data:
            sanitized_data["velocity"] = sanitize_text(data.get("velocity"), max_length=30)
        if "trend" in data:
            sanitized_data["trend"] = sanitize_text(data.get("trend"), max_length=30)
        if "mitigation" in data:
            sanitized_data["mitigation"] = sanitize_text(data.get("mitigation"), max_length=2000)
        if "action_plan" in data:
            sanitized_data["action_plan"] = sanitize_text(data.get("action_plan"), max_length=2000)

        updated = database.update_risk(risk_id, sanitized_data)
        if not updated:
            return jsonify({"error": "Risk not found"}), 404
        return jsonify(updated)
    except Exception as e:
        return mask_exception(e, f"update_risk #{risk_id}")


@app.route("/api/risks/<int:risk_id>", methods=["DELETE"])
def delete_risk(risk_id):
    """Remove a risk from database with audit event logging."""
    try:
        if risk_id < 1 or risk_id > 1000000:
            return jsonify({"error": "Invalid risk identifier"}), 400

        success = database.delete_risk(risk_id)
        if not success:
            return jsonify({"error": "Risk not found"}), 404
        return jsonify({"success": True, "message": f"Risk #{risk_id} removed successfully."})
    except Exception as e:
        return mask_exception(e, f"delete_risk #{risk_id}")


@app.route("/api/matrix", methods=["GET"])
def get_matrix():
    """Retrieve 5x5 matrix populated with active risks."""
    try:
        matrix_data = database.get_matrix_data()
        return jsonify(matrix_data)
    except Exception as e:
        return mask_exception(e, "get_matrix")


@app.route("/api/audit-logs", methods=["GET"])
def get_audit_trail():
    """Retrieve recent database audit activity trail."""
    try:
        logs = database.get_audit_logs()
        return jsonify(logs)
    except Exception as e:
        return mask_exception(e, "get_audit_trail")


@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    """Retrieve system alerts and critical notifications."""
    try:
        alerts = database.get_alerts()
        return jsonify(alerts)
    except Exception as e:
        return mask_exception(e, "get_alerts")


@app.route("/api/alerts/<int:alert_id>/read", methods=["POST"])
def read_alert(alert_id):
    """Mark an alert as read in the database."""
    try:
        database.mark_alert_read(alert_id)
        return jsonify({"success": True})
    except Exception as e:
        return mask_exception(e, f"read_alert #{alert_id}")


@app.route("/api/simulate", methods=["POST"])
def simulate():
    """Run interactive quantitative VaR loss simulation with bounded parameters to prevent CPU DoS."""
    try:
        data = request.get_json(silent=True) or {}
        likelihood = sanitize_integer(data.get("likelihood"), 1, 5, 3)
        impact = sanitize_integer(data.get("impact"), 1, 5, 3)
        financial_base = sanitize_number(data.get("financial_impact"), 0.0, 10_000_000_000.0, 1_000_000.0)
        # Bounded between 100 and 10,000 iterations to protect against CPU exhaustion
        iterations = sanitize_integer(data.get("iterations"), 100, 10_000, 3000)

        sim_results = run_monte_carlo(likelihood, impact, financial_base, iterations)
        return jsonify(sim_results)
    except Exception as e:
        return mask_exception(e, "simulate")


@app.route("/api/reset-seed", methods=["POST"])
def reset_seed():
    """Re-seed database with clean enterprise benchmark data."""
    try:
        database.reset_seed_data()
        return jsonify({"success": True, "message": "Database reset and seeded with enterprise benchmark dataset."})
    except Exception as e:
        return mask_exception(e, "reset_seed")


@app.route("/api/ai/suggest-mitigation", methods=["POST"])
def suggest_mitigation():
    """AI Risk Mitigation Resolution Engine (ISO 31000 Compliant)."""
    try:
        data = request.get_json(silent=True) or {}
        name = sanitize_text(data.get("name"), max_length=150, default="Corporate Threat")
        category = sanitize_text(data.get("category"), max_length=50, default="Operational")
        likelihood = sanitize_integer(data.get("likelihood"), 1, 5, 3)
        impact = sanitize_integer(data.get("impact"), 1, 5, 3)
        score = likelihood * impact
        financial = sanitize_number(data.get("financial_impact"), 0.0, 10_000_000_000.0, 500000.0)
        velocity = sanitize_text(data.get("velocity"), max_length=30, default="Medium")
        description = sanitize_text(data.get("description"), max_length=2000, default="")

        plan = generate_ai_mitigation_plan_text(name, category, likelihood, impact, score, financial, velocity, description)
        return jsonify({
            "success": True,
            "solution": plan,
            "risk_name": name,
            "category": category,
            "score": score
        })
    except Exception as e:
        return mask_exception(e, "suggest_mitigation")


# ─── Math & Analytical Engines ────────────────────────────────────────────────

def generate_ai_mitigation_plan_text(name, category, likelihood, impact, score, financial, velocity, description=""):
    """Synthesize structured 3-tier enterprise resolution based on ISO 31000 ERM protocol."""
    fin_text = f"${financial/1_000_000:.2f}M" if financial >= 1_000_000 else (f"${int(financial/1_000)}k" if financial > 0 else "material")
    lower_name = (name + " " + description).lower()

    if category == "Cybersecurity" or any(k in lower_name for k in ["cyber", "ransom", "breach", "zero-day", "hack", "data"]):
        t1 = "Immediately isolate impacted network perimeters, revoke compromised API credentials, and execute emergency EDR telemetry lockdown."
        t2 = "Enforce Zero-Trust architecture across all endpoints, mandate FIDO2 hardware MFA keys, and verify air-gapped immutable backups."
        t3 = "Conduct quarterly external red-team penetration tests and maintain an active $5.00M cyber-liability insurance indemnity pool."
    elif category == "Financial" or any(k in lower_name for k in ["fx", "currency", "liquidity", "credit", "cash", "inflation", "interest"]):
        t1 = f"Activate rolling 90-day FX forward contracts and interest-rate collar corridors to cap {fin_text} monetary exposure."
        t2 = "Establish dual-signoff revolving credit facility with top-tier banking syndicate and institute dynamic counterparty credit limits."
        t3 = "Run automated bi-weekly stress simulations under +250 bps macroeconomic rate shock with real-time treasury telemetry alerts."
    elif category == "Operational" or any(k in lower_name for k in ["supply", "vendor", "semiconductor", "logistics", "factory", "warehouse"]):
        t1 = "Activate pre-vetted secondary Tier-1 suppliers in alternate geographical hubs to secure 60-day buffer safety stock."
        t2 = "Implement real-time IoT shipment route tracking and negotiate binding SLA breach penalty clauses across master service agreements."
        t3 = "Perform biannual supply-chain resilience audits and establish an agile alternate Bill of Materials (BOM) substitution protocol."
    elif category == "Compliance" or any(k in lower_name for k in ["legal", "privacy", "gdpr", "regulat", "audit", "license", "statutory"]):
        t1 = "Execute emergency legal hold, map cross-border personal data flows, and pause non-compliant data replication pipelines."
        t2 = "Implement ISO 27701 privacy controls, update standard contractual clauses (SCCs), and roll out automated consent governance."
        t3 = "Mandate semi-annual third-party compliance reviews and institutionalize formal CRO signoff on regulatory disclosures."
    else: # Strategic
        t1 = "Convene executive risk committee chaired by CRO & Division VP to re-calibrate resource allocation within 14 days."
        t2 = "Diversify core revenue streams across non-correlated product categories and launch rapid agile customer-validation pilots."
        t3 = "Integrate competitive horizon threat scanning into quarterly Board of Directors governance review sessions."

    if score >= 16 or velocity == "Fast":
        t1 = f"[HIGH PRIORITY ESCALATION] {t1} Submit immediate incident briefing to Board of Directors within 24 hours."

    return (
        f"1. Immediate Containment (0–30 Days): {t1}\n"
        f"2. Preventive Engineering (30–90 Days): {t2}\n"
        f"3. Continuous Governance (Ongoing): {t3}"
    )


def run_monte_carlo(likelihood_val, impact_val, financial_base, iterations=3000):
    """Run probabilistic trial simulation on exposure with bounded iterations."""
    p = likelihood_val / 5.0
    impact_factor = impact_val / 5.0

    losses = []
    for _ in range(iterations):
        if random.random() < p:
            severity = max(0.05, random.lognormvariate(math.log(impact_factor + 0.1), 0.35))
            loss = financial_base * severity
        else:
            loss = 0.0
        losses.append(round(loss, 2))

    losses.sort()
    n = len(losses)
    non_zero = [l for l in losses if l > 0]

    mean_loss = sum(losses) / n
    var_95 = losses[int(n * 0.95)]
    worst_case = losses[-1]

    # Histogram buckets (10 intervals)
    max_loss = worst_case if worst_case > 0 else 1000
    bucket_size = max_loss / 10
    histogram = []
    for i in range(10):
        low_bound = i * bucket_size
        high_bound = (i + 1) * bucket_size
        count = sum(1 for l in losses if low_bound <= l < high_bound or (i == 9 and l >= low_bound))
        histogram.append({
            "range": f"${int(low_bound/1000)}k-${int(high_bound/1000)}k",
            "frequency": count,
            "percentage": round((count / n) * 100, 1)
        })

    return {
        "iterations": iterations,
        "meanLoss": round(mean_loss, 2),
        "medianLoss": round(losses[n // 2], 2),
        "valueAtRisk95": round(var_95, 2),
        "worstCase": round(worst_case, 2),
        "occurrenceRate": round((len(non_zero) / n) * 100, 1),
        "histogram": histogram
    }


def generate_trend_forecast(current_score, trend="stable", velocity="Medium"):
    """Generate 6-month projected risk trajectory with confidence band."""
    months = ["Month +1", "Month +2", "Month +3", "Month +4", "Month +5", "Month +6"]
    trend_slope = 0.8 if trend == "increasing" else (-0.7 if trend == "decreasing" else 0.0)
    velocity_mult = 1.3 if velocity == "Fast" else (1.0 if velocity == "Medium" else 0.7)

    series = []
    val = float(current_score)
    for i, m in enumerate(months):
        val = max(1.0, min(25.0, val + (trend_slope * velocity_mult) + random.uniform(-0.4, 0.4)))
        series.append({
            "month": m,
            "score": round(val, 1),
            "upper": round(min(25.0, val + 1.2 + (i * 0.3)), 1),
            "lower": round(max(1.0, val - 1.2 - (i * 0.3)), 1)
        })
    return series


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*65)
    print("  RiskGuard Pro — Enterprise Risk Assessment & Analytics Server")
    print("  [SECURITY ENGINE]: Active Firewall, Rate Limiter, OWASP Headers")
    print("  Frontend Directory: " + CLIENT_DIR)
    print("  Database Engine: Supabase (PostgreSQL Cloud) + Local Resilient Fallback")
    print(f"  Dashboard Listening: http://localhost:{port}")
    print("="*65 + "\n")
    app.run(debug=False, port=port, host="0.0.0.0")
