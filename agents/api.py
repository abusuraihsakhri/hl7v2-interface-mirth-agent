"""
FastAPI REST API Server for Hl7V2 Interface Mirth Agent.
"""
import os
import hmac
from contextlib import asynccontextmanager
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException, GLOBAL_AUDIT
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """A publicly reachable service must never sign records using the development fallback key."""
    secret = os.environ.get("AUDIT_SECRET_KEY", "")
    if len(secret) < 32 or secret == "your-secure-audit-key-here":
        raise RuntimeError("Set AUDIT_SECRET_KEY to a strong, unique secret (at least 32 characters) before serving.")
    if not hmac.compare_digest(GLOBAL_AUDIT.secret_key, secret.encode("utf-8")):
        raise RuntimeError("Configure AUDIT_SECRET_KEY before importing the application.")
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Hl7V2 Interface Mirth Agent API",
    description="Enterprise Distributed Component Platform (Clinical & Biomedical AI)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "hl7v2-interface-mirth-agent", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Potential personal identifier detected. Use synthetic identifiers.")
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
