# Clinical Trial Document Generation System

> **RAG-Powered** · **Groq LLM** · **React + Vite** · **ICH E6/E3** · **FDA/EMA Compliant**

A full-stack application for automated generation of regulatory-grade clinical trial documents
(CSP, ICF, CSR, SAP) with an interactive React frontend, FastAPI backend, FAISS vector store,
and human-in-the-loop review workflow.

---

## Quick Start (5 minutes)

```bash
# 1. Clone & enter
git clone <repo> && cd ctdgen-full

# 2. Backend
cp .env.example .env
# Edit .env → set GROQ_API_KEY=gsk_...
pip install -r requirements.txt
python app.py                         # → http://localhost:8765

# 3. Frontend (new terminal)
cd frontend/ctdgen-ui
npm install
npm run dev                           # → http://localhost:5173
```

Open **http://localhost:5173** in your browser.

---

## Project Structure

```
ctdgen-full/
│
├── app.py                         ← FastAPI entry point
├── requirements.txt
├── Dockerfile / docker-compose.yml
├── .env.example                   ← Copy to .env
├── pytest.ini
│
├── backend/
│   ├── core/
│   │   ├── groq_client.py         ★ GroqClient — callable LLM interface
│   │   ├── models.py              ★ All Pydantic schemas
│   │   └── config.py             ★ Pydantic-settings config
│   │
│   ├── services/
│   │   ├── rag_service.py         ★ FAISS ingestion & retrieval
│   │   ├── generation_service.py  ★ Section-by-section LLM generation
│   │   └── compliance_service.py  ★ Regulatory rule validation + NER
│   │
│   ├── api/
│   │   ├── routes.py              ★ All FastAPI endpoints
│   │   └── dependencies.py       ★ DI container (lru_cache singletons)
│   │
│   ├── db/
│   │   └── session_store.py       In-memory TTL session store
│   │
│   └── utils/
│       └── helpers.py             Text utilities, Markdown export
│
├── frontend/
│   └── ctdgen-ui/                 Vite + React application
│       ├── src/
│       │   ├── App.jsx            Router + layout shell
│       │   ├── main.jsx
│       │   ├── index.css          Global design system (dark theme)
│       │   ├── store/
│       │   │   └── appStore.js    Zustand global state
│       │   ├── services/
│       │   │   └── api.js         Axios API service layer
│       │   ├── components/
│       │   │   ├── ui/            Button, Badge, Card, Input, Select…
│       │   │   ├── layout/        Sidebar, Topbar
│       │   │   ├── forms/         StudyMetadataForm (full user spec)
│       │   │   ├── document/      GenerationProgress, DocumentViewer
│       │   │   ├── feedback/      FeedbackMechanism (HITL)
│       │   │   └── compliance/    CompliancePanel
│       │   └── pages/
│       │       ├── GeneratePage   ★ Main workflow (form→progress→review)
│       │       ├── ReviewPage     Document viewer + multi-format export
│       │       ├── FeedbackPage   Full HITL review management
│       │       ├── IngestPage     File upload + text paste to FAISS
│       │       ├── CompliancePage Standalone compliance report
│       │       ├── AnalyticsPage  Charts, quality metrics, gauges
│       │       └── SettingsPage   User profile + API config
│       └── vite.config.js
│
├── scripts/
│   └── generate_cli.py            CLI for offline generation
│
└── tests/
    ├── unit/
    │   ├── test_groq_client.py    13 unit tests
    │   └── test_compliance.py     11 unit tests
    └── integration/
        └── test_pipeline.py       10 integration tests (mocked Groq)
```

---

## Frontend Pages

| Page | Route | Description |
|------|-------|-------------|
| Generate | `/` | Main 3-step wizard: form → progress → review |
| Review | `/review` | Section viewer with MD/TXT/JSON export |
| Feedback | `/feedback` | HITL review log, filter, submit feedback |
| Ingest | `/ingest` | Drag-drop file upload + paste text to FAISS |
| Compliance | `/compliance` | Standalone compliance report with score ring |
| Analytics | `/analytics` | Word counts, confidence bars, quality gauges |
| Settings | `/settings` | User profile, role, API config, preferences |

---

## Backend API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Server + Groq + vector store status |
| POST | `/api/v1/generate` | Generate full document (main endpoint) |
| POST | `/api/v1/ingest/document` | Upload PDF/TXT to vector store |
| POST | `/api/v1/ingest/metadata` | Add structured metadata to vector store |
| GET | `/api/v1/sessions/{id}` | Retrieve session data |
| POST | `/api/v1/compliance/{id}` | Re-run compliance check |
| POST | `/api/v1/feedback/{id}` | Submit HITL reviewer feedback |
| POST | `/api/v1/finalize/{id}` | Finalize document after review |
| GET | `/api/v1/templates` | Available document templates |
| GET | `/api/v1/vector-store` | FAISS vector store statistics |

Interactive Swagger UI: **http://localhost:8765/docs**

---

## GroqClient Calling Patterns

```python
from backend.core.groq_client import GroqClient

client = GroqClient()                              # reads GROQ_API_KEY from env

# Simple chat
client("Write intro for Phase III oncology")       # __call__ shorthand
client.chat("prompt")
client.chat_with_system("system prompt", "user prompt")

# Streaming
for chunk in client.stream("Generate a long section..."):
    print(chunk, end="", flush=True)

# Batch (with rate-limit spacing)
results = client.batch(["prompt1", "prompt2", "prompt3"])

# JSON mode
import json
data = json.loads(client.json_chat("Return JSON with study fields"))

# Availability
client.is_available()   # True when GROQ_API_KEY is set
repr(client)            # <GroqClient model=llama-3.3-70b-versatile available=True>
```

---

## Generation Request Example

```json
POST /api/v1/generate
{
  "metadata": {
    "indication": "Oncology",
    "phase": "Phase III",
    "design": "Randomized, Controlled, Double-blind",
    "primary_endpoint": "Overall Survival (OS)",
    "secondary_endpoints": ["PFS", "ORR", "QoL"],
    "patient_population": "Adults with HER2-positive metastatic breast cancer",
    "sample_size": 520,
    "duration_months": 48,
    "investigational_product": "TrialDrug-X 150mg",
    "sponsor": "PharmaCo Inc.",
    "therapeutic_area": "Oncology"
  },
  "document_type": "Clinical Study Protocol",
  "rag_top_k": 5,
  "model_tier": "medical",
  "include_compliance_check": true
}
```

---

## Supported Document Types

| Type | Abbr | Sections | Standards |
|------|------|----------|-----------|
| Clinical Study Protocol | CSP | 9 | ICH E6(R2), E8, FDA 21 CFR 312 |
| Informed Consent Form | ICF | 8 | ICH E6, 45 CFR 46, FDA 21 CFR 50 |
| Clinical Study Report | CSR | 8 | ICH E3, EMA Module 5 |
| Statistical Analysis Plan | SAP | 8 | ICH E9(R1), FDA Statistical Guidance |

---

## Groq Models

| Tier | Model | Use Case |
|------|-------|----------|
| `fast` | llama-3.1-8b-instant | High volume, quick drafts |
| `default` | llama-3.3-70b-versatile | General generation |
| `medical` | llama-3.3-70b-versatile | **Recommended** for clinical docs |

---

## Environment Variables

```bash
# Required
GROQ_API_KEY=gsk_...

# Optional (defaults shown)
GROQ_MODEL=medical
API_PORT=8765
VECTOR_DIM=384
RAG_TOP_K=5
LOG_LEVEL=INFO
ENABLE_NER=false
```

---

## Docker

```bash
# Full stack
GROQ_API_KEY=gsk_... docker compose up

# API only
docker build -t ctdgen-api .
docker run -e GROQ_API_KEY=gsk_... -p 8765:8765 ctdgen-api
```

---

## Run Tests

```bash
# All tests (34 total)
pytest tests/ -v

# Unit only
pytest tests/unit/ -v

# Integration only
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=backend --cov-report=html
```

---

## CLI Usage

```bash
python scripts/generate_cli.py \
  --indication Oncology \
  --phase "Phase III" \
  --design "Randomized, Controlled, Double-blind" \
  --endpoint "Overall Survival (OS)" \
  --population "Adults with HER2-positive metastatic breast cancer" \
  --drug "TrialDrug-X 150mg" \
  --doc-type "Clinical Study Protocol" \
  --output ./output/protocol.md
```

---

## Compliance Validation

Scoring: **Critical** −15 pts · **Warning** −5 pts · **Info** −1 pt

| Score | Status |
|-------|--------|
| ≥ 85 | Ready for sponsor review |
| 70 – 84 | Minor issues to address |
| < 70 | Significant revision required |

---

## Disclaimer

This system generates **draft** clinical trial documents only.
All output must be reviewed by qualified medical writers, biostatisticians,
and regulatory affairs specialists before submission.
Generated content does not constitute regulatory advice.
