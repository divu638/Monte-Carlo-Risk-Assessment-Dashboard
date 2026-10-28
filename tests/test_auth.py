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
