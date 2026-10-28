"""
Test Suite: Enterprise Security & OWASP Hardening (17/17 Test Cases)
Verifies:
- OWASP Defense-in-Depth Headers
- Server Cloaking & Fingerprint Masking
- Anti-Path-Traversal & Sensitive File Exposure Shields (.env, .git, *.py, *.db)
- Input Sanitization & Stored-XSS Neutralization
- Parameter Bounds Enforcement
- Sliding-Window Rate Limiting
"""

import pytest
import os
import sys

# Ensure server path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))
from app import app
import database


@pytest.fixture
def client():
    app.config["TESTING"] = True
    database.init_db()
    with app.test_client() as client:
        yield client


# ─── 1 to 6: OWASP Defense-in-Depth Headers ──────────────────────────────────

def test_01_owasp_csp_header_present(client):
    """Test 1: Content-Security-Policy header is present and enforces default-src."""
    res = client.get("/")
    assert "Content-Security-Policy" in res.headers
    csp = res.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp


def test_02_owasp_x_frame_options_sameorigin(client):
    """Test 2: Anti-Clickjacking X-Frame-Options is set to SAMEORIGIN."""
    res = client.get("/")
    assert res.headers.get("X-Frame-Options") == "SAMEORIGIN"


def test_03_owasp_x_content_type_options_nosniff(client):
    """Test 3: Anti-MIME-Sniffing header is set to nosniff."""
    res = client.get("/")
    assert res.headers.get("X-Content-Type-Options") == "nosniff"


def test_04_owasp_referrer_policy(client):
    """Test 4: Referrer-Policy enforces strict-origin-when-cross-origin."""
    res = client.get("/")
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_05_owasp_permissions_policy(client):
    """Test 5: Permissions-Policy disables unnecessary browser device sensors."""
    res = client.get("/")
    assert "Permissions-Policy" in res.headers
    perm = res.headers["Permissions-Policy"]
    assert "geolocation=()" in perm


def test_06_owasp_x_xss_protection(client):
    """Test 6: X-XSS-Protection legacy filter is enabled with mode=block."""
    res = client.get("/")
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"


# ─── 7: Server Cloaking ──────────────────────────────────────────────────────

def test_07_server_banner_cloaking(client):
    """Test 7: Server fingerprint hides Werkzeug/Python version banner."""
    res = client.get("/")
    server_header = res.headers.get("Server", "")
    assert "Werkzeug" not in server_header
    assert "Python" not in server_header
    assert "Enterprise-Risk-Security-Gateway" in server_header


# ─── 8 to 12: Sensitive File & Path Traversal Shields ────────────────────────

def test_08_block_env_file_probing(client):
    """Test 8: Access to .env credentials is blocked with 403 Forbidden."""
    res = client.get("/.env")
    assert res.status_code == 403


def test_09_block_git_directory_probing(client):
    """Test 9: Access to .git repository internal files is blocked with 403."""
    res = client.get("/.git/config")
    assert res.status_code == 403


def test_10_block_python_source_code_probing(client):
    """Test 10: Access to backend Python source code (.py) is blocked with 403."""
    res = client.get("/server/app.py")
    assert res.status_code == 403


def test_11_block_sqlite_db_probing(client):
    """Test 11: Access to raw SQLite database file (.db) is blocked with 403."""
    res = client.get("/server/riskguard.db")
    assert res.status_code == 403


def test_12_block_path_traversal_dot_dot(client):
    """Test 12: Path traversal probes (../) escape attempts are blocked with 403."""
    res = client.get("/../../etc/passwd")
    assert res.status_code == 403


# ─── 13: Stored XSS Neutralization ───────────────────────────────────────────

def test_13_input_sanitization_stored_xss(client):
    """Test 13: HTML tags (<script>) in input payloads are neutralized/escaped."""
    payload = {
        "name": "<script>alert('XSS')</script>Test Vulnerability",
        "description": "<img src=x onerror=alert(1)>",
        "category": "Operational",
        "likelihood": 3,
        "impact": 3
    }
    res = client.post("/api/risks", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert "<script>" not in data["name"]
    assert "&lt;script&gt;" in data["name"]


# ─── 14 to 16: Input Bounds Enforcement ──────────────────────────────────────

def test_14_parameter_bounds_enforcement_likelihood(client):
    """Test 14: Likelihood input outside 1-5 is clamped safely."""
    payload = {
        "name": "Extreme Likelihood Risk",
        "category": "Financial",
        "likelihood": 999,
        "impact": 3
    }
    res = client.post("/api/risks", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["likelihood"] == 5  # Clamped to max allowed 5


def test_15_parameter_bounds_enforcement_impact(client):
    """Test 15: Impact input below 1 is clamped to 1."""
    payload = {
        "name": "Negative Impact Risk",
        "category": "Compliance",
        "likelihood": 2,
        "impact": -10
    }
    res = client.post("/api/risks", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["impact"] == 1  # Clamped to min allowed 1


def test_16_parameter_bounds_enforcement_iterations(client):
    """Test 16: Monte Carlo simulation iterations are clamped between 100 and 10,000 to prevent CPU DoS."""
    payload = {
        "likelihood": 3,
        "impact": 3,
        "financial_impact": 1000000,
        "iterations": 1000000  # Attempt 1 Million iterations
    }
    res = client.post("/api/simulate", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["iterations"] <= 10000


# ─── 17: Sliding-Window Rate Limiting ────────────────────────────────────────

def test_17_sliding_window_rate_limiting(client):
    """Test 17: Rapid burst write requests trigger IP rate limit response."""
    # Rate limit for 'reset' endpoint is 5 requests per 60 seconds
    hit_rate_limit = False
    for _ in range(12):
        res = client.post("/api/reset-seed")
        if res.status_code == 429:
            hit_rate_limit = True
            break
    assert hit_rate_limit is True
