import pytest

from agents.base import AuditTrail


def test_hmac_audit_integrity_and_content_tampering():
    trail = AuditTrail(secret_key="test-only-unique-key")
    trail.log("operator", "supervisor", "CHECK", {"status": "SUCCESS"})
    trail.log("operator", "supervisor", "CHECK", {"status": "RETRY"})
    assert trail.verify_integrity() is True

    trail.logs[0]["payload_hash"] = "0" * 64
    assert trail.verify_integrity() is False


def test_hmac_audit_rejects_forged_signature():
    trail = AuditTrail(secret_key="test-only-unique-key")
    trail.log("operator", "supervisor", "CHECK", {"status": "SUCCESS"})
    trail.logs[0]["current_hash"] = "0" * 64
    assert trail.verify_integrity() is False


def test_hmac_audit_rejects_corrupted_chain():
    trail = AuditTrail(secret_key="test-only-unique-key")
    trail.log("operator", "supervisor", "CHECK", {"status": "SUCCESS"})
    trail.log("operator", "supervisor", "CHECK", {"status": "RETRY"})
    trail.logs[1]["prev_hash"] = "unrelated"
    assert trail.verify_integrity() is False
