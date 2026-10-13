# HL7 v2 Interface Mirth Agent

A browser-based HL7 v2 structural preflight inspector, alongside Python demonstration tools for synthetic metric auditing. The browser tool does **not** connect to Mirth Connect and does not require a Python server.

## Browser inspector

Open `web/index.html` through a static HTTP server, or use GitHub Pages when the Pages deployment is enabled.

- Paste one HL7 v2 ER7 message, or import a `.hl7` / `.txt` file of up to 1 MiB.
- Inspect MSH fields, segment formatting, and selected PID, OBR, and OBX fields.
- Accept conventional CR or LF line endings and optional outer MLLP framing.
- Report structural errors and warnings; download a JSON findings summary without the raw message.
- Run entirely in the browser without sending input to an external service.

The checker is **not** a full version-specific HL7 conformance validator, an HL7 interface engine, a Mirth channel auditor, or a HIPAA Safe Harbor de-identification tool. It does not deliver or acknowledge HL7 messages. Do not use its results for clinical decisions or production message acceptance without independent validation.

For local development:

```bash
python -m http.server 8080
# Open http://localhost:8080/web/
```

The site requires modern browser support for JavaScript modules, Blob downloads, and the File API. No Pyodide or browser Python runtime is needed because the checks run in JavaScript.

## Python CLI and API

The Python code provides **separate synthetic-metric demonstrations** (not HL7 segment parsing). Both the root `cli.py` / `agents/` stack and the `hl7v2_interface_mirth_agent/` package remain available.

```bash
python -m pip install -e ".[test]"
python -m pytest -q

# Root CLI: synthetic-metric audit, CSV batch, chat, audit verification
python cli.py audit --task-id DEMO-001 --target SYNTHETIC-01 --primary 28.5 --secondary 14.2 --critical
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit

# Installed package CLI (different input schema)
hl7v2-interface-mirth-engine audit --case-id DEMO-001 --primary 15 --secondary 5
```

For the local FastAPI service, supply a **unique, random** signing key of at least 32 characters. The service refuses to start with a missing or example key:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python cli.py serve --host 127.0.0.1 --port 8000
# GET /health, GET /metrics, POST /api/audit, POST /api/chat, GET /api/audit/logs
```

Or copy `.env.example`, replace the placeholder `AUDIT_SECRET_KEY`, and run `docker compose up --build`. Compose binds port 8000 to localhost by default. The Docker container serves the Python API, **not** the static browser application.

## Security and privacy

- **Browser:** message content is processed in memory in the active tab. The site has no analytics, third-party scripts, remote calls, or application-managed persistence. Exported JSON reports contain only aggregated segment counts and diagnostic findings.
- **Python:** synthetic audit data and HMAC-chained log entries are held in process memory. The audit-chain verifier checks signatures and links. Development-only CLI use without `AUDIT_SECRET_KEY` falls back to an insecure test key; never rely on that key for audit authenticity.
- **Limitations:** the Python API has no user authentication and the regex-based PHI checks are incomplete. Do not expose it to the public internet, submit real patient data, or claim regulatory compliance without additional controls and independent security review. Demo thresholds are not medically validated clinical cutoffs.

## Testing

```bash
python -m pip install -e ".[test]"
python -m pytest -q
python -m pip check
node --test web/hl7.test.mjs
```

GitHub Actions checks Python 3.10–3.12 and the browser inspection module. GitHub Pages deploys the static files only.

## Technology and license

Python 3.9+ (FastAPI, Pydantic v2, Uvicorn), HTML/CSS/modern JavaScript, Node.js for browser-module tests, and optional Docker. MIT license; see [LICENSE](LICENSE).
