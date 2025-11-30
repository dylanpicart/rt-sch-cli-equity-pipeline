# RAG Service – Semantic Q&A for SVI + School Climate

This submodule contains the **FastAPI-based RAG (Retrieval-Augmented Generation) service** that sits on top of the dbt-modeled Snowflake **Gold** layer and SVI tract data. It provides natural-language equity insights backed by:

- Climate survey questions
- Metric definitions
- SVI definitions and vulnerability scores
- District-level response-rate metrics

The service exposes:

- `POST /api/rag/query` – multi-mode RAG endpoint
- `GET /api/status` – backend mode & model configuration

and powers the **`rag-ui/` React/TypeScript frontend**.

---

## Features

- **Multi-mode RAG**:
  - `district_risk_overview` – district-level SVI + climate risk overview
  - `explain_metric` – interpret metrics (e.g. student/parent response rate)
  - `explain_question` – deep-dive on climate survey questions
  - `compare_districts` – equity-focused comparison between two districts

- **Semantic layer integration**:
  - `GOLD.DIM_CLIMATE_QUESTION`
  - `GOLD.DIM_CLIMATE_METRIC_DEFINITION`
  - `GOLD.DIM_SVI_DEFINITION`
  - `BRONZE_GOLD.GOLD_CLIMATE_VULNERABILITY`
  - `GOLD.SCHOOL_CLIMATE_SNAPSHOT` (optional metrics)

- **Vector search** via Chroma over ~5,400 embedded text chunks

- **Dev vs Prod modes**:
  - Fake embeddings + fake LLM → offline, zero-cost testing
  - Real embeddings + OpenAI LLM → full semantic behavior

---

## RAG Architecture (ASCII Overview)

```text
GOLD.DIM_CLIMATE_QUESTION
GOLD.DIM_CLIMATE_METRIC_DEFINITION
GOLD.DIM_SVI_DEFINITION
BRONZE_GOLD.GOLD_CLIMATE_VULNERABILITY
GOLD.SCHOOL_CLIMATE_SNAPSHOT (optional metrics)
                    │
                    ▼
         rag_service.ingest (Python)
  - Fetch text from Snowflake GOLD/BRONZE_GOLD
  - Normalize into semantic chunks
  - Embed via OpenAI or FakeEmbeddings
                    │
                    ▼
       Chroma Vector Store (data/chroma_index)
                    │
                    ▼
  LangChain Retriever + Prompt Library (prompts.py)
  - district_risk_overview
  - explain_metric
  - explain_question
  - compare_districts
                    │
                    ▼
     FastAPI RAG API (rag_service/api.py)
  - POST /api/rag/query
  - GET  /api/status
                    │
                    ▼
 React/TypeScript UI (rag-ui/)
 - Mode selector (overview / metric / question)
 - District & year filters
 - Answer + bullets + metrics + citations
````

---

## RAG Architecture (Mermaid Diagram)

```mermaid
flowchart TB
    subgraph Snowflake_Gold["Snowflake Gold + SVI"]
        Q[DIM_CLIMATE_QUESTION]
        M[DIM_CLIMATE_METRIC_DEFINITION]
        SVI[DIM_SVI_DEFINITION]
        VULN[BRONZE_GOLD.GOLD_CLIMATE_VULNERABILITY]
        SNAP[SCHOOL_CLIMATE_SNAPSHOT]
    end

    Snowflake_Gold --> INGEST[rag_service.ingest<br/>(embedding + upsert)]
    INGEST --> VDB[Chroma Vector DB<br/>(data/chroma_index)]

    VDB --> RETRIEVER[LangChain Retriever<br/>+ Prompt Library (prompts.py)]
    SNAP --> RETRIEVER

    RETRIEVER --> API[FastAPI RAG API<br/>(api.py, langchain_chain.py)]
    API --> UI[React/TypeScript UI<br/>(rag-ui)]

    subgraph Modes
        O[district_risk_overview]
        EM[explain_metric]
        EQ[explain_question]
        CD[compare_districts]
    end

    API --> O
    API --> EM
    API --> EQ
    API --> CD
```

---

## Dev vs Prod Modes

The service can run in **offline** or **real** modes using environment variables (in the project root `.env`):

```env
# Embeddings
USE_FAKE_EMBEDDINGS=true   # true → FakeEmbeddings; false → OpenAI embeddings

# LLM
USE_FAKE_LLM=true          # true → FakeChatLLM; false → OpenAI ChatCompletion
```

* `USE_FAKE_EMBEDDINGS=true` – uses deterministic local vectors, no OpenAI embedding cost
* `USE_FAKE_LLM=true` – uses canned structured responses, no OpenAI completion calls

When you’re ready to run with real models:

```env
USE_FAKE_EMBEDDINGS=false
USE_FAKE_LLM=false
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-large
```

Then:

```bash
# Rebuild embeddings with real model
python -m rag_service.ingest

# Start backend
uvicorn rag_service.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Endpoints

### `GET /api/status`

Returns the server’s current mode and models:

```json
{
  "use_fake_embeddings": true,
  "use_fake_llm": true,
  "embedding_model": "text-embedding-3-large",
  "llm_model": "gpt-4.1-mini"
}
```

### `POST /api/rag/query`

Example request:

```json
{
  "question": "Provide a district-level risk and equity overview for District 29 using SVI and climate data.",
  "district_id": 29,
  "other_district_id": 30,   // optional for compare_districts
  "year": 2024,
  "mode": "district_risk_overview"
}
```

Example response shape:

```json
{
  "answer": "High-level narrative...",
  "high_level_bullets": [
    "Theme: ... – Metric: ... – Explanation: ...",
    "..."
  ],
  "metrics": [
    {
      "metric_name": "Average Parent Response Rate",
      "value": 0.42,
      "year": null,
      "source": "SCHOOL_CLIMATE.GOLD.SCHOOL_CLIMATE_SNAPSHOT"
    }
  ],
  "citations": [
    {
      "id": "svi_tract::36081000100",
      "source_type": "svi_tract",
      "source_id": "36081000100"
    }
  ]
}
```

---

## Running Locally

From project root:

```bash
# Backend (FastAPI)
uvicorn rag_service.main:app --host 0.0.0.0 --port 8000 --reload
```

From `rag-ui/`:

```bash
npm install
npm run dev
```

Then open: `http://localhost:5173`.

---
