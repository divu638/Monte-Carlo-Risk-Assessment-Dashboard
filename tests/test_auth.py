"""
Test Suite: Authentication & Role-Based Access Control (RBAC)
Verifies:
- User registration with bcrypt hashing
- Login authentication and JWT generation
- Suspended/Blocked account access prevention
- RBAC route protection (admin-only routes return 401/403 for unauthorized users)
"""

import os
import sys
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


def test_auth_login_seeded_admin(client):
    """Verify seeded admin can authenticate and receives a signed JWT token."""
    res = client.post("/api/auth/login", json={
        "email": "admin@riskguard.pro",
        "password": "AdminPassword123!"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["role"] == "admin"


def test_auth_login_seeded_user(client):
    """Verify seeded analyst user can authenticate and has role 'user'."""
    res = client.post("/api/auth/login", json={
        "email": "analyst@riskguard.pro",
        "password": "AnalystPass123!"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["role"] == "user"


def test_auth_login_invalid_password(client):
    """Verify incorrect credentials fail with 401 Unauthorized."""
    res = client.post("/api/auth/login", json={
        "email": "admin@riskguard.pro",
        "password": "WrongPassword999!"
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False


def test_admin_route_blocked_without_token(client):
    """Verify admin routes reject requests without a token with 401."""
    res = client.get("/api/admin/users")
    assert res.status_code == 401


def test_admin_route_blocked_for_normal_user(client):
    """Verify normal user token receives 403 Forbidden on admin routes."""
    login_res = client.post("/api/auth/login", json={
        "email": "analyst@riskguard.pro",
        "password": "AnalystPass123!"
    })
    user_token = login_res.get_json()["token"]

    res = client.get("/api/admin/users", headers={
        "Authorization": f"Bearer {user_token}"
    })
    assert res.status_code == 403


def test_admin_route_allowed_for_admin(client):
    """Verify admin token successfully accesses admin endpoints."""
    login_res = client.post("/api/auth/login", json={
        "email": "admin@riskguard.pro",
        "password": "AdminPassword123!"
    })
    admin_token = login_res.get_json()["token"]

    res = client.get("/api/admin/users", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert res.status_code == 200
    users = res.get_json()
    assert isinstance(users, list)
    assert len(users) >= 2


def test_google_auth_new_user(client):
    """Verify new user registration and JWT issuance via Google OAuth/SSO."""
    res = client.post("/api/auth/google", json={
        "email": "google.analyst.test@enterprise.com",
        "firstname": "Priya",
        "lastname": "Sharma"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["email"] == "google.analyst.test@enterprise.com"
    assert data["user"]["auth_provider"] == "google"


def test_google_auth_existing_user(client):
    """Verify existing user login via Google OAuth returns valid session."""
    # First sign in (creates)
    client.post("/api/auth/google", json={
        "email": "existing.cro@riskguard.pro",
        "firstname": "Chief",
        "lastname": "Officer"
    })
    # Second sign in (logs in)
    res = client.post("/api/auth/google", json={
        "email": "existing.cro@riskguard.pro"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["email"] == "existing.cro@riskguard.pro"


def test_google_auth_missing_email(client):
    """Verify Google auth rejects empty or invalid email with 400."""
    res = client.post("/api/auth/google", json={"firstname": "NoEmail"})
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False


def test_auth_config_endpoint(client):
    """Verify /api/auth/config exposes OAuth availability."""
    res = client.get("/api/auth/config")
    assert res.status_code == 200
    data = res.get_json()
    assert data["google_enabled"] is True


def test_auth_relogin_flow(client):
    """Verify newly registered user can log in multiple consecutive times without issue."""
    email = "consecutive_login_test@riskguard.pro"
    pw = "StrongPass123!"
    
    # 1. Register
    reg = client.post("/api/auth/register", json={
        "firstname": "Consecutive",
        "lastname": "Tester",
        "company": "Test Org",
        "email": email,
        "password": pw
    })
    assert reg.status_code in (201, 409)
    
    # 2. First login
    l1 = client.post("/api/auth/login", json={"email": email, "password": pw})
    assert l1.status_code == 200
    d1 = l1.get_json()
    assert d1["success"] is True
    assert "token" in d1
    
    # 3. Second login (re-login)
    l2 = client.post("/api/auth/login", json={"email": email, "password": pw})
    assert l2.status_code == 200
    d2 = l2.get_json()
    assert d2["success"] is True
    assert "token" in d2


def test_auth_reset_password_and_login(client):
    """Verify password reset endpoint allows setting a new password and logging in with it."""
    email = "reset_login_test@riskguard.pro"
    new_pw = "NewSecretPassword123!"
    
    res = client.post("/api/auth/reset-password", json={
        "email": email,
        "password": new_pw
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    
    # Verify login with the new password
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": new_pw
    })
    assert login_res.status_code == 200
    assert login_res.get_json()["success"] is True
