"""
Integration Tests for RiskGuard Pro REST API Endpoints:
- Financial Ratios & Benchmark Telemetry (B2, B3)
- Rule-based Solutions Engine (B4)
- Stress Testing & Scenario Simulation (B5)
- Explainable Risk Score (B6)
- Action Task Register (B7)
- Cybersecurity Posture Evaluation (B9)
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))
from app import app
import database


@pytest.fixture
def client():
    app.config["TESTING"] = True
    database.init_db()
    with app.test_client() as client:
        yield client


def test_api_benchmarks(client):
    """Verify benchmark fetch returns industry dictionary."""
    resp = client.get("/api/benchmarks")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True
    assert "Manufacturing" in data["benchmarks"]
    assert "current_ratio" in data["benchmarks"]["Manufacturing"]


def test_api_calculate_ratios(client):
    """Verify financial ratio calculation API returns full suite and Altman Z."""
    payload = {
        "data": {
            "current_assets": 400,
            "current_liabilities": 200,
            "total_assets": 1000,
            "total_debt": 400,
            "total_equity": 600,
            "revenue": 1200,
            "gross_profit": 360,
            "net_profit": 120,
            "ebit": 180,
            "interest_expense": 30,
            "inventory": 80,
            "accounts_receivable": 100
        },
        "industry": "Manufacturing"
    }
    resp = client.post("/api/ratios/calculate", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True
    results = data["results"]
    assert results["liquidity"]["current_ratio"] == 2.0
    assert results["leverage"]["de_ratio"] == round(400 / 600, 2)
    assert "altman_z" in results
    assert "benchmark_comparisons" in results


def test_api_solutions_recommend(client):
    """Verify rule-based solution engine returns 3-tier actionable plans."""
    payload = {
        "ratios": {
            "liquidity": {"current_ratio": 0.82, "quick_ratio": 0.45},
            "leverage": {"de_ratio": 3.8, "interest_coverage": 1.1},
            "altman_z": {"zone": "Distress Zone", "score": 1.35}
        }
    }
    resp = client.post("/api/solutions/recommend", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True
    assert data["count"] >= 2
    rule_ids = [s["rule_id"] for s in data["solutions"]]
    assert "LIQ-001" in rule_ids


def test_api_stress_test(client):
    """Verify stress test endpoint applies shocks and runs Monte Carlo simulation."""
    payload = {
        "base_financials": {
            "revenue": 5000000,
            "total_debt": 2000000,
            "total_equity": 3000000,
            "total_assets": 5000000
        },
        "base_health_score": 80.0,
        "base_var_exposure": 800000.0,
        "revenue_shock_pct": -20.0,
        "debt_increase_pct": 15.0,
        "cost_inflation_pct": 10.0,
        "iterations": 2000
    }
    resp = client.post("/api/stress-test", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True
    metrics = data["stress_results"]["stressed_metrics"]
    assert metrics["health_score"] < 80.0
    assert metrics["var_95"] > 0


def test_api_stress_presets(client):
    """Verify stress test presets list returns standard scenarios."""
    resp = client.get("/api/stress-test/presets")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert "recession" in data["presets"]
    assert "ransomware" in data["presets"]


def test_api_explain_score(client):
    """Verify explainable score returns waterfall steps and domain breakdown."""
    payload = {
        "assessment": {
            "company_name": "Acme Global",
            "health_score": 72.0,
            "step_data": {}
        },
        "ratios": {
            "liquidity": {"current_ratio": 1.1},
            "leverage": {"de_ratio": 2.1}
        }
    }
    resp = client.post("/api/score/explain", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True
    assert "waterfall_steps" in data["explanation"]
    assert "domains" in data["explanation"]


def test_api_action_tasks_crud(client):
    """Verify action task creation, retrieval, and status updates."""
    # Create task
    new_task = {
        "title": "Deploy Hardware MFA on Core Jump Hosts",
        "description": "FIDO2 security key enforcement across infrastructure",
        "category": "Cybersecurity",
        "priority": "Critical",
        "treatment_type": "Reduce",
        "cost_estimate": "₹1.5 Lakhs",
        "due_date": "2026-11-30"
    }
    resp = client.post("/api/tasks", json=new_task)
    assert resp.status_code == 201
    data = json.loads(resp.data)
    assert data["success"] is True
    task_id = data["task"]["id"]

    # Get tasks
    get_resp = client.get("/api/tasks")
    assert get_resp.status_code == 200
    tasks_data = json.loads(get_resp.data)
    assert any(t["id"] == task_id for t in tasks_data["tasks"])

    # Update task
    upd_resp = client.put(f"/api/tasks/{task_id}", json={"status": "In Progress"})
    assert upd_resp.status_code == 200

    # Delete task
    del_resp = client.delete(f"/api/tasks/{task_id}")
    assert del_resp.status_code == 200


def test_api_cyber_evaluate(client):
    """Verify cyber posture endpoint computes CVSS score and ALE."""
    payload = {
        "ransomware_resilience": 5.0,
        "data_breach_prevention": 6.0,
        "vulnerability_exposure": 5.0,
        "access_control_iam": 6.0,
        "backup_recovery": 7.0,
        "annual_revenue": 100000000
    }
    resp = client.post("/api/cyber/evaluate", json=payload)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True
    posture = data["cyber_posture"]
    assert 0 <= posture["cvss_composite_score"] <= 10
    assert posture["annualized_loss_expectancy"] > 0
    assert "monte_carlo_feed" in posture
