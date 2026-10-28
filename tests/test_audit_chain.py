"""
Test Suite: Tamper-Evident SHA-256 Audit Chain Verification
Verifies:
- Append-only cryptographic hash chain
- Zero-tampering verification passing on valid data
- Immediate detection and identification of modified or injected rows
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))
import database


@pytest.fixture(autouse=True)
def setup_db():
    database.init_db()


def test_audit_chain_valid():
    """Verify that the seeded and recorded audit chain passes cryptographic integrity."""
    report = database.verify_audit_chain()
    assert report["valid"] is True
    assert report["total_records"] > 0
    assert "Zero tampering detected" in report["message"]


def test_audit_chain_record_and_chain():
    """Verify that adding a new audit record correctly chains to previous hash."""
    prev_hash = database.get_last_audit_hash()
    new_hash = database.record_audit_log(
        risk_id=999,
        risk_name="Test Threat",
        action="CREATED",
        details="Security chain test event",
        user_id=1
    )
    assert new_hash is not None
    assert new_hash != prev_hash

    report = database.verify_audit_chain()
    assert report["valid"] is True
    assert report["head_hash"] == new_hash


def test_audit_chain_tamper_detection():
    """Verify that modifying an existing record breaks the cryptographic chain."""
    conn = database.get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM audit_logs ORDER BY id ASC LIMIT 1")
    row = cur.fetchone()
    assert row is not None, "Audit logs must not be empty"
    target_id = row[0] if isinstance(row, (tuple, list)) else row["id"]

    # Maliciously tamper with an existing row's action
    cur.execute("UPDATE audit_logs SET details = 'MALICIOUS_TAMPERED_CONTENT' WHERE id = ?", (target_id,))
    conn.commit()
    conn.close()

    report = database.verify_audit_chain()
    assert report["valid"] is False
    assert report["tampered_at_id"] == target_id
    assert "mismatch" in report["reason"].lower() or "broken" in report["reason"].lower()

    # Restore database seed for other tests
    database.reset_seed_data()
