import asyncio
import math

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from agents.api import api_audit, app, lifespan
from agents.models import SystemTaskPayload


def test_api_rejects_phi_with_client_error():
    payload = SystemTaskPayload(
        task_id="TEST", target_identifier="MRN-123456", primary_metric=10
    )
    with pytest.raises(HTTPException) as exc:
        api_audit(payload)
    assert exc.value.status_code == 422
    assert "MRN-123456" not in str(exc.value.detail)


def test_nonfinite_metric_is_invalid():
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="TEST", target_identifier="SYNTH-01", primary_metric=math.inf)


def test_public_service_requires_explicit_audit_secret(monkeypatch):
    monkeypatch.delenv("AUDIT_SECRET_KEY", raising=False)

    async def start_app():
        async with lifespan(app):
            pass

    with pytest.raises(RuntimeError, match="AUDIT_SECRET_KEY"):
        asyncio.run(start_app())
