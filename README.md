# Hl7v2 Interface Mirth Agent

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Hl7v2 Interface Mirth Agent** is an analytical platform implementing LIS/HIS MSH/PID/OBR/OBX Stream Inspector & Safe Harbor Sanitizer. It provides:

- **Multi-worker evaluation pipeline** with specialized agents for QC, safety, and protocol conformance
- **Zero-PHI outbound interceptor** blocking SSNs, MRNs, phone numbers, and patient identifiers
- **Tamper-evident HMAC-SHA256 audit trail** with chained cryptographic signatures
- **FastAPI REST API** with OpenAPI 3.1 spec and Prometheus metrics
- **CLI** for single evaluations, batch CSV processing, and interactive chat

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/hl7v2-interface-mirth-agent.git
cd hl7v2-interface-mirth-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`MessageHierarchyValidatorAgent`**: Primary metric & baseline quality auditor.
- **`OBXResultAuditorAgent`**: STAT kinetics & closed-loop escalation auditor.
- **`HIPAASafeHarborSanitizerAgent`**: Biomarker & concordance triager.

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Interactive Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task/case identifier (required)
- `--target`: Target identifier (required)
- `--primary`: Primary metric value (float)
- `--secondary`: Secondary metric value (float)
- `--critical`: Trigger emergency/critical flag
- `--status`: Status descriptor (e.g., NOMINAL, DISCORDANT)

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- `AUDIT_SECRET_KEY` — HMAC-SHA256 signing key (generate a strong random key)
- `MODEL_PROVIDER` — LLM provider: `mock`, `ollama`, `claude`, `openai`

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 100
```

---

## 🐳 Container Deployment

### Docker
```bash
docker build -t hl7v2-interface-mirth-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key hl7v2-interface-mirth-agent
```

### Docker Compose
```bash
# Create .env file with required variables
cp .env.example .env
# Edit .env and set AUDIT_SECRET_KEY

docker-compose up -d
```

---

## 📁 Project Structure

```
├── agents/                          # Core agent modules
│   ├── api.py                       # FastAPI REST server
│   ├── base.py                      # PHI guard, audit trail, security
│   ├── models.py                    # Pydantic schemas
│   ├── supervisor.py                # Multi-worker orchestrator
│   ├── workers.py                   # Specialized evaluation workers
│   └── ...
├── hl7v2_interface_mirth_agent/     # Alternative implementation package
├── tests/                           # Test suite
├── cli.py                           # CLI entry point
├── simulator.py                     # Load testing simulator
├── enrichment.py                    # Feature enrichment suite
├── Dockerfile                       # Container build
├── docker-compose.yml               # Container orchestration
└── pyproject.toml                   # Project metadata
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
