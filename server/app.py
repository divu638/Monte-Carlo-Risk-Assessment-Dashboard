"""
Flask REST API Server for RiskGuard Pro
Serves static frontend from ../client and connects to Supabase (PostgreSQL Cloud)
with built-in local resilience fallback.
"""

import os
import sys
import random
import math
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import database

# Load env
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Paths
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIR = os.path.abspath(os.path.join(SERVER_DIR, "..", "client"))

app = Flask(__name__, static_folder=CLIENT_DIR, static_url_path="")
CORS(app)

# Ensure database is initialized
database.init_db()

# ─── Static File Serving ──────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve main dashboard client HTML."""
    return send_from_directory(CLIENT_DIR, "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    """Serve CSS, JS, and client assets."""
    return send_from_directory(CLIENT_DIR, filename)

# ─── REST API Endpoints ───────────────────────────────────────────────────────

@app.route("/api/db-status", methods=["GET"])
def get_db_status():
    """Retrieve database engine status, provider, and Supabase connectivity."""
    try:
        status = database.get_connection_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/config/supabase", methods=["POST"])
def configure_supabase():
    """Configure and test Supabase credentials dynamically from the UI."""
    data = request.get_json() or {}
    url = data.get("url", "")
    key = data.get("key", "")
    sync_data = data.get("sync_data", True)

    if not url or not key:
        return jsonify({"success": False, "error": "Both Supabase Project URL and API Key are required."}), 400

    result = database.configure_supabase_credentials(url, key, sync_data=sync_data)
    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Retrieve executive KPIs, distribution, and health score."""
    try:
        stats = database.get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/risks", methods=["GET"])
def list_risks():
    """Retrieve risks with optional filters (category, level, status, search)."""
    category = request.args.get("category")
    level = request.args.get("level")
    status = request.args.get("status")
    search = request.args.get("search")

    try:
        risks = database.get_all_risks(category=category, level=level, status=status, search=search)
        return jsonify(risks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/risks/<int:risk_id>", methods=["GET"])
def get_risk(risk_id):
    """Get single risk details with Monte Carlo and trend projection."""
    try:
        risk = database.get_risk_by_id(risk_id)
        if not risk:
            return jsonify({"error": "Risk not found"}), 404

        # Monte Carlo loss projection
        financial = float(risk.get("financial_impact", 100000.0) or 100000.0)
        sim = run_monte_carlo(int(risk["likelihood"]), int(risk["impact"]), financial)
        forecast = generate_trend_forecast(int(risk["score"]), risk.get("trend", "stable"), risk.get("velocity", "Medium"))

        return jsonify({
            **risk,
            "simulation": sim,
            "forecast": forecast
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/risks", methods=["POST"])
def add_risk():
    """Create a new risk in database with audit log."""
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Risk name is required"}), 400

    try:
        new_risk = database.create_risk(data)
        return jsonify(new_risk), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/risks/<int:risk_id>", methods=["PUT"])
def update_risk(risk_id):
    """Update risk details and audit trail in database."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No update payload provided"}), 400

    try:
        updated = database.update_risk(risk_id, data)
        if not updated:
            return jsonify({"error": "Risk not found"}), 404
        return jsonify(updated)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/risks/<int:risk_id>", methods=["DELETE"])
def delete_risk(risk_id):
    """Remove a risk from database and log the event."""
    try:
        success = database.delete_risk(risk_id)
        if not success:
            return jsonify({"error": "Risk not found"}), 404
        return jsonify({"success": True, "message": f"Risk #{risk_id} deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/matrix", methods=["GET"])
def get_matrix():
    """Retrieve 5x5 matrix populated with active risks."""
    try:
        matrix_data = database.get_matrix_data()
        return jsonify(matrix_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/audit-logs", methods=["GET"])
def get_audit_trail():
    """Retrieve recent database audit activity trail."""
    try:
        logs = database.get_audit_logs()
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    """Retrieve system alerts and critical notifications."""
    try:
        alerts = database.get_alerts()
        return jsonify(alerts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/alerts/<int:alert_id>/read", methods=["POST"])
def read_alert(alert_id):
    """Mark an alert as read in the database."""
    try:
        database.mark_alert_read(alert_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/simulate", methods=["POST"])
def simulate():
    """Run interactive Monte Carlo loss simulation."""
    data = request.get_json() or {}
    likelihood = int(data.get("likelihood", 3))
    impact = int(data.get("impact", 3))
    financial_base = float(data.get("financial_impact", 1000000.0))
    iterations = int(data.get("iterations", 3000))

    sim_results = run_monte_carlo(likelihood, impact, financial_base, iterations)
    return jsonify(sim_results)

@app.route("/api/reset-seed", methods=["POST"])
def reset_seed():
    """Re-seed database with clean enterprise data."""
    try:
        database.reset_seed_data()
        return jsonify({"success": True, "message": "Database reset and seeded with enterprise dataset"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Math & Analytical Engines ────────────────────────────────────────────────

def run_monte_carlo(likelihood_val, impact_val, financial_base, iterations=3000):
    """Run probabilistic Monte Carlo trial simulation on exposure."""
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
    print("  Monte Carlo Risk Engine -- Enterprise Risk Assessment Server")
    print("  Frontend Served From: " + CLIENT_DIR)
    print("  Database: Supabase (PostgreSQL Cloud) + Local Fallback")
    print(f"  Dashboard URL: http://localhost:{port}")
    print("="*65 + "\n")
    app.run(debug=False, port=port, host="0.0.0.0")
