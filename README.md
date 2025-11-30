# **Real-Time Batch & Streaming ELT Pipeline**

<!-- Row 1 -->
[![CI Status](https://github.com/dylanpicart/rt-sch-cli-equity-pipeline/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/dylanpicart/rt-sch-cli-equity-pipeline/actions/workflows/ci.yml)
![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)
![dbt Core](https://img.shields.io/badge/dbt-Core%201.1x-orange)
![Terraform](https://img.shields.io/badge/Terraform-IaC-purple)
![MIT License](https://img.shields.io/badge/License-MIT-green)

<!-- Row 2 -->
![FastAPI](https://img.shields.io/badge/FastAPI-API%20Service-009688?logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-RAG%20Orchestration-1C3C3C)
![Chroma](https://img.shields.io/badge/Chroma-Vector%20DB-orange)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react&logoColor=black)
![Snowflake](https://img.shields.io/badge/Snowflake-Data%20Warehouse-29B5E8?logo=snowflake&logoColor=white)
![Databricks](https://img.shields.io/badge/Databricks-Spark%20Workspace-EF3E34?logo=databricks&logoColor=white)
![GCP](https://img.shields.io/badge/GCP-Cloud%20Platform-4285F4?logo=google-cloud&logoColor=white)

## **Kafka · Databricks · Snowflake · dbt · FastAPI · LangChain · Chroma · React/TypeScript · Power BI · GCP · Terraform · CI/CD**

> **Project Status:** Production-ready.

* Full CI/CD + IaC + DevSecOps pipeline implemented
* Dashboard live; Databricks–Snowflake connector and job orchestration finalized
* dbt semantic layer (SVI definitions, climate questions, metric dictionary, vulnerability tables)
* AI analytics layer with multi-mode RAG service (district risk overview, metric explanation, survey question analysis, district comparison)
* FastAPI microservices + status/health endpoints
* Chroma vector database with 5K+ embedded documents
* React/TypeScript UI for natural-language district equity insights

---

## **Table of Contents**

* [Project Overview](#project-overview)
* [Purpose](#purpose)
* [Architecture Overview](#architecture-overview)
* [Quick Start (Local Simulation)](#quick-start-local-simulation)
  * [1. Create virtual environment](#1-create-virtual-environment)
  * [2. Copy example variables](#2-copy-example-variables)
  * [3. Run batch ingestion (local)](#3-run-batch-ingestion-local)
  * [4. Run mock streaming ingestion (local)](#4-run-mock-streaming-ingestion-local)
* [Databricks Integration](#databricks-integration)
* [Terraform Infrastructure-as-Code (IaC)](#terraform-infrastructure-as-code-iac)
  * [**GCP**](#gcp)
  * [**Snowflake**](#snowflake)
  * [**Databricks**](#databricks)
  * [**Environment separation**](#environment-separation)
  * [Local workflow](#local-workflow)
* [RAG Service – Semantic Q\&A for SVI + School Climate](#rag-service--semantic-qa-for-svi--school-climate)
  * [Data sources used by the RAG layer](#data-sources-used-by-the-rag-layer)
  * [dbt seeds (semantic layer)](#dbt-seeds-semantic-layer)
  * [RAG service architecture](#rag-service-architecture)
  * [Dev vs Prod modes](#dev-vs-prod-modes)
  * [Running the RAG backend](#running-the-rag-backend)
  * [Frontend (rag-ui)](#frontend-rag-ui)
* [What RAG Adds](#what-rag-adds)
* [Why This Matters](#why-this-matters)
* [CI (Continuous Integration)](#ci-continuous-integration)
  * [**Pre-commit hooks**](#pre-commit-hooks)
    * [**Tests**](#tests)
    * [**dbt validation**](#dbt-validation)
    * [**Terraform validation**](#terraform-validation)
* [CD (Continuous Delivery — Manual Only)](#cd-continuous-delivery--manual-only)
* [Security (DevSecOps)](#security-devsecops)
* [Roadmap](#roadmap)
* [License](#license)
* [Author](#author)

---

## Project Overview

This project is a **modern, end-to-end data platform** that unifies streaming, batch, semantic modeling, and AI-assisted analytics.
It demonstrates how **Kafka, Databricks, dbt, and Snowflake** integrate in a **Medallion Architecture (Bronze → Silver → Gold)** to power **equity-focused insights** across NYC School Climate and Social Vulnerability Index (SVI) data.

On top of the ELT pipeline, the project adds a lightweight **Retrieval-Augmented Generation (RAG) service** using **FastAPI, LangChain, Chroma, and React/TypeScript**. This semantic layer enables district leaders to ask natural-language questions—*“What are the top risk indicators for District 29?”*—and receive grounded, contextual answers backed by dbt-validated Gold tables.

Built as part of the **Data Engineering Modern Toolkit** initiative, the system showcases real-world engineering practices across cloud infrastructure, CI/CD, DevSecOps, semantic modeling, and AI-driven data experiences.

---

## Purpose

Many organizations still rely on siloed spreadsheets and manual workflows.
This project demonstrates how to modernize those workflows using:

* **Streaming ingestion** (Kafka → GCS Bronze)
* **Distributed compute** (Databricks Spark)
* **Automated SQL transformations** (dbt)
* **Cloud warehousing** (Snowflake)
* **Cross-platform orchestration** (Databricks Jobs + GitHub Actions)
* **Enterprise-ready monitoring & visualization** (Power BI)

The result is a **scalable, reproducible, and secure** ELT pipeline suitable for real-world data engineering environments.

---

## Architecture Overview

```text
         ┌──────────────────────────┐     ┌──────────────────────────┐
         │          Kafka           │     │        REST API          │
         │   (Real-time Streaming)  │     │     (Batch Ingestion)    │
         └──────────────┬───────────┘     └──────────────┬───────────┘
                        │                                │
                        └──────────────┬─────────────────┘
                                       ▼
                               Bronze (Raw)
                            GCS Landing Zone
                                       ▼
              ┌───────────────────────────────┬──────────────────────────────┐
              │                               │                              │
              ▼                               ▼                              │
   ┌────────────────────────┐      ┌──────────────────────────────┐          │
   │  Databricks (Spark     │      │        Dataproc (Batch)      │          │
   │ Structured Streaming + │      │  SVI ingestion + large-scale │          │
   │       Batch ETL)       │      │        PySpark transforms    │          │
   └────────────────────────┘      └──────────────────────────────┘          │
              └───────────────────────────────┬──────────────────────────────┘
                                               ▼
                                     Silver (Cleaned)
                               Delta / Parquet stored in GCS
                                               ▼
                                    dbt → Snowflake (Gold)
                              (Semantic Models + Metrics Layer)
                                               ▼
        ┌──────────────────────────────┬────────────────────────────┬────────────────────┐
        ▼                              ▼                            ▼                    ▼
 Power BI Dashboard        FastAPI RAG Service (LLM)           APIs / Apps           Other Consumers
 (District Equity KPIs)    (Semantic Q&A on Gold Layer)

```

```mermaid
flowchart TB
    subgraph Sources
        K[Kafka\n(Real-time Streaming)]
        R[REST API\n(Batch Ingestion)]
    end

    K --> B[Bronze (Raw)\nGCS Landing Zone]
    R --> B

    subgraph Compute
        D[Databricks\nSpark Structured Streaming\n+ Batch ETL]
        P[Dataproc\nBatch SVI Ingestion\n+ PySpark Transforms]
    end

    B --> D
    B --> P
    D --> S[Silver (Cleaned)\nDelta/Parquet on GCS]
    P --> S

    S --> G[dbt → Snowflake (Gold)\nSemantic Models + Metrics]

    subgraph Consumers
        PB[Power BI Dashboard\nEquity KPIs]
        RAG[FastAPI RAG Service\n(LLM Semantic Q&A)]
        OC[Other Consumers / APIs\nDownstream Pipelines]
    end

    G --> PB
    G --> RAG
    G --> OC```

---

### Medallion Layers

* **Bronze** – Unprocessed, schema-flexible raw data
* **Silver** – Cleaned, normalized, typed Delta/Parquet
* **Gold** – dbt-modeled analytical tables powering dashboards

A detailed architecture diagram is found in `/diagrams/`.

---

## Technologies

**Languages** – Python, SQL
**Streaming** – Kafka (Confluent)
**Compute** – Databricks (Spark Structured Streaming)
**Storage** – GCS (Bronze/Silver)
**Warehouse** – Snowflake
**Transformations** – dbt
**Orchestration** – Databricks Jobs, GitHub Actions
**API / Services** – FastAPI (RAG microservice)
**AI / RAG** – LangChain, OpenAI API (LLM & embeddings), Chroma (vector DB)
**Frontend** – React, TypeScript, Vite
**Visualization** – Power BI
**DevOps** – Terraform (IaC), Makefile, pre-commit, detect-secrets

---

## Repository Structure

```text
rt-sch-cli-equity-pipeline/
│
├── README.md
├── SECURITY.md
├── .gitignore
├── .env.example
├── Makefile
├── pyproject.toml
├── pre-commit-config.yaml
├── LICENSE
│
├── infra/                   # IaC for GCP, Snowflake, Databricks
│   └── terraform/
│       ├── main.tf
│       ├── providers.tf
│       ├── variables.tf
│       ├── gcs.tf
│       ├── snowflake.tf
│       ├── databricks.tf
│       ├── dataproc.tf
│       ├── gcp_snowflake_integration.tf
│       ├── terraform.tfvars.example
│       └── terraform.dev.tfvars (ignored)
│
├── dbt/                     # dbt semantic modeling (Bronze → Silver → Gold)
│   ├── models/
│   │   ├── bronze/
│   │   ├── silver/
│   │   └── gold/
│   ├── seeds/
│   ├── tests/
│   └── macros/
│
├── dataproc/                # Batch SVI ingestion jobs (PySpark)
│   ├── jobs/
│   │   └── load_svi_to_snowflake.py
│   ├── kafka_streaming.py
│   └── config/
│
├── rag_service/             # FastAPI RAG microservice
│   ├── main.py
│   ├── api.py
│   ├── prompts.py
│   ├── langchain_chain.py
│   ├── embeddings.py
│   ├── ingest.py
│   ├── vector_store.py
│   └── config.py
│
├── rag-ui/                  # React/TypeScript RAG frontend
│   ├── public/
│   ├── src/
│   ├── vite.config.ts
│   └── .env.local (ignored)
│
├── kafka/                   # Local Kafka producer for mock streaming
│   ├── kafka_producer.py
│   └── config/
│
├── rt_databricks/           # Mirror of Databricks repo - Structured streaming + batch transforms
│
├── scripts/                 # Utility + integration scripts
│   ├── gcp/
│   ├── snowflake/
│   └── utilities/
│
├── powerbi/
├── diagrams/
└── screenshots/

```

---

## Quick Start (Local Simulation)

> **No real credentials are committed. .env and *.tfvars are gitignored.**

### 1. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Copy example variables

```bash
cp infra/terraform/terraform.tfvars.example infra/terraform/terraform.dev.tfvars
cp config/secrets.example.yml config/secrets.local.yml
```

### 3. Run batch ingestion (local)

```bash
python scripts/gcp/fetch_svi_to_gcs.py
```

### 4. Run mock streaming ingestion (local)

```bash
python scripts/streaming/mock_stream.py
```

---

## Databricks Integration

Databricks powers the **real-time streaming** and large-scale batch side:

* Kafka → Bronze streaming pipelines via Spark Structured Streaming
* Bronze → Silver cleaning using notebook-driven transformations
* Silver → Snowflake Gold sync via Snowflake connector
* Databricks Secret Scopes for secure GCP + Snowflake integration
* Configurable job cluster defined via **Terraform**
* Orchestration via Databricks Jobs (auto-paused)

---

## Terraform Infrastructure-as-Code (IaC)

Terraform (in `infra/terraform/`) provisions the entire data platform:

### **GCP**

* GCS Bronze/Silver/Gold buckets
* Snowflake GCS service account
* IAM bindings for integration
* Optional Dataproc cluster (feature-flagged)

### **Snowflake**

* Warehouse: `PIPELINE_WH`
* Database: `SCHOOL_CLIMATE`
* Schemas: `BRONZE`, `SILVER`, `GOLD`, `DBT_DYLAN`
* Roles: `PIPELINE_ROLE`, `BI_ROLE`
* Grants: USAGE / ALL PRIVILEGES / SELECT via classic provider
* Storage Integration + External Stage for Bronze

### **Databricks**

* Job definition for Bronze → Silver transformations
* Job cluster (Spark runtime, node specs)

### **Environment separation**

* `terraform.dev.tfvars` (ignored)
* `terraform.tfvars.example`
* Flags:

  * `enable_databricks_job`
  * `enable_dataproc_cluster`

### Local workflow

```bash
cd infra/terraform
set -a && source ../../.env && set +a
terraform fmt
terraform init -backend=false
terraform validate
terraform plan -var-file="terraform.dev.tfvars"
```

---

## RAG Service – Semantic Q&A for SVI + School Climate

This project includes a lightweight Retrieval-Augmented Generation (RAG) service that sits on top of the **GOLD** semantic layer and SVI tract data to provide leadership-friendly natural language answers to equity questions.

It supports multiple modes:

* `district_risk_overview` – high-level risk + equity overview for a district
* `explain_metric` – deep dive on what a metric means and why it matters
* `explain_question` – deep dive on a climate survey question
* `compare_districts` – equity-focused comparison of two districts (API-only for now)

### Data sources used by the RAG layer

The RAG service reads from:

* `GOLD.DIM_CLIMATE_QUESTION`
  Semantic question dimension (group, domain, short/full text, response scale).

* `GOLD.DIM_CLIMATE_METRIC_DEFINITION`
  Metric definitions (label, group, definition, formula, source table, grain).

* `GOLD.DIM_SVI_DEFINITION`
  SVI semantic layer (overall SVI, theme names/descriptions, bucket logic).

* `BRONZE_GOLD.GOLD_CLIMATE_VULNERABILITY`
  Tract-level SVI scores: `SVI_OVERALL_SCORE`, `SVI_OVERALL_BUCKET`, `RPL_THEME1–4`.

* `GOLD.SCHOOL_CLIMATE_SNAPSHOT` (optional)
  District-level climate metrics:
  * `PARENT_RESPONSE_RATE`
  * `TEACHER_RESPONSE_RATE`
  * `STUDENT_RESPONSE_RATE`
  * `DISTRICT_NUMBER`, `DBN`

If `SCHOOL_CLIMATE_SNAPSHOT` is missing or inaccessible, the service degrades gracefully and responds without numeric metrics.

### dbt seeds (semantic layer)

The semantic layer is managed via dbt seeds:

* `dbt/seeds/svi/dim_svi_definition.csv` → `GOLD.DIM_SVI_DEFINITION`
* `dbt/seeds/climate/dim_climate_metric_definition.csv` → `GOLD.DIM_CLIMATE_METRIC_DEFINITION`
* `dbt/seeds/climate/dim_climate_question.csv` → `GOLD.DIM_CLIMATE_QUESTION`

To (re)seed:

```bash
cd dbt
dbt seed --select dim_svi_definition dim_climate_metric_definition dim_climate_question \
  --profiles-dir ../.dbt
```

### RAG service architecture

```text
GOLD.DIM_CLIMATE_QUESTION
GOLD.DIM_CLIMATE_METRIC_DEFINITION
GOLD.DIM_SVI_DEFINITION
BRONZE_GOLD.GOLD_CLIMATE_VULNERABILITY
                    │
                    ▼
           rag_service.ingest
      (builds text corpus + embeddings)
                    │
                    ▼
         Chroma vector store (data/chroma_index)
                    │
                    ▼
           LangChain retriever + LLM
                    │
                    ▼
    FastAPI (/api/rag/query, /api/status) → React UI (rag-ui)
```

### Dev vs Prod modes

The RAG service supports both **offline/dev mode** and **real model mode** via environment flags in `.env`:

```env
# Embeddings
USE_FAKE_EMBEDDINGS=true  # or false for real embeddings via OpenAI

# LLM
USE_FAKE_LLM=true         # or false for real LLM completions
```

* **Fake embeddings (`USE_FAKE_EMBEDDINGS=true`)**

  * Uses a deterministic local `FakeEmbeddings` class
  * No OpenAI embedding calls
  * Good for testing ingestion, retrieval, and UI wiring

* **Fake LLM (`USE_FAKE_LLM=true`)**

  * Uses `FakeChatLLM`, which returns canned but structured text
  * No OpenAI completion calls
  * Perfect for offline dev / demos without any API usage

When you’re ready to use real models:

1. Set billing limits in OpenAI (e.g., soft: $3, hard: $10).

2. Flip the flags in `.env`:

   ```env
   USE_FAKE_EMBEDDINGS=false
   USE_FAKE_LLM=false
   ```

3. Rebuild embeddings once:

   ```bash
   python -m rag_service.ingest
   ```

4. Restart the backend:

   ```bash
   uvicorn rag_service.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Running the RAG backend

From project root:

```bash
# Load env vars (including USE_FAKE_* and SNOWFLAKE_*):
set -a
source .env
set +a

# Start the API
uvicorn rag_service.main:app --host 0.0.0.0 --port 8000 --reload
```

Key endpoints:

* `GET /api/status`
  Returns backend mode:

  ```json
  {
    "use_fake_embeddings": true,
    "use_fake_llm": true,
    "embedding_model": "text-embedding-3-large",
    "llm_model": "gpt-4.1-mini"
  }
  ```

* `POST /api/rag/query`
  Body:

  ```json
  {
    "question": "Provide a district-level risk and equity overview for District 29 using SVI and climate data.",
    "district_id": 29,
    "other_district_id": 30,        // optional, for compare_districts
    "year": 2024,
    "mode": "district_risk_overview"
    // one of: "district_risk_overview", "explain_metric", "explain_question", "compare_districts"
  }
  ```

  Response:

  ```json
  {
    "answer": "High-level narrative...",
    "high_level_bullets": ["Theme: ... – Metric: ... – Explanation: ...", "..."],
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

### Frontend (rag-ui)

The frontend lives in `rag-ui/` and talks to the RAG backend via Vite env vars:

* `rag-ui/.env.local`:

  ```env
  VITE_API_BASE_URL=http://localhost:8000
  VITE_FAKE_MODE=true   # purely for UI labeling; backend is authoritative
  ```

To run the UI:

```bash
cd rag-ui
npm install   # first time
npm run dev
```

Then visit: `http://localhost:5173`

UI features:

* Mode selector:

  * `District risk overview`
  * `Explain a metric`
  * `Explain a question`
* District + year filters
* “Sample question” buttons per mode
* “Ask” + “Clear” controls
* Status badges:

  * BACKEND: REAL/FAKE based on `/api/status`
  * FRONTEND FAKE FLAG: based on `VITE_FAKE_MODE`

## What RAG Adds

* Semantic retrieval over climate + SVI domain knowledge
* District-specific metrics pulled live from Snowflake
* Human-readable equity explanations
  * Risk indicators
  * Metric interpretation
  * Survey question analysis
  * Optional district comparisons
* Multiple modes:
  * district_risk_overview
  * explain_metric
  * explain_question
  * compare_districts

## Why This Matters

RAG transforms the pipeline from a traditional ETL/ELT system into a decision-support tool:

* Leadership can ask complex equity questions in plain English
* Responses remain grounded in real district data
* dbt ensures all definitions and metrics are consistent and validated
* The semantic index makes unstructured domain context instantly searchable

---

## CI (Continuous Integration)

Located at `.github/workflows/ci.yml`.

Runs on **every push + PR**:

### **Pre-commit hooks**

* whitespace cleanup
* EOF fixes
* YAML validation
* **detect-secrets** scan
* `black` formatting
* `ruff` & `flake8` linting

#### **Tests**

* `pytest` (unit + integration)

#### **dbt validation**

* `dbt deps`
* `dbt compile` (using a dummy CI profile—no Snowflake calls made)

#### **Terraform validation**

* `terraform fmt -check`
* `terraform init -backend=false`
* `terraform validate`

All CI checks run **without secrets**.

---

## CD (Continuous Delivery — Manual Only)

Located at `.github/workflows/cd.yml`.

A **manual `workflow_dispatch`** that supports:

* Running dbt against **Snowflake**
* Running dbt against **Databricks**
* Optional `terraform apply`
* Per-environment (`dev` or `prod`)
* Credentials loaded from **GitHub Secrets** (never in Git)

This ensures deployments are **explicit, safe, and auditable**.

---

## Security (DevSecOps)

See `SECURITY.md` for full policy.

Key features:

* No credentials committed — `.env`, `*.tfvars`, and service accounts are gitignored
* `detect-secrets` guards the repo from accidental exposure
* Terraform providers pinned to prevent supply-chain drift
* CI/CD workflows segregated (CI = validate only, CD = manual apply)
* Principle-of-least-privilege Snowflake & GCP roles

---

## Roadmap

* \[\] Add detailed table-level lineage diagram (Bronze → Silver → Gold, SVI + Climate models)
* \[\] Add automated integration test suite (end-to-end tests hitting dev Snowflake / GCS)
* \[\] Add Databricks Jobs API orchestration (trigger + monitor jobs via REST/SDK)
* \[\] Add Docker local environment for reproducible dev + CI
* \[\] Add Power BI refresh automation (triggered after successful ELT runs)
* \[\] Integrate SVI dashboard and merge SVI data with School Climate data for cross-referenced equity analysis

---

## License

This project is released under the **MIT License**.
You are free to use, modify, and distribute this project for personal or commercial purposes.
See the [LICENSE](LICENSE) file for full details.

---

## Author

Developed by **Dylan Picart** at Partnership With Children
**Data Engineer · Analytics Engineer · AI/ML Practitioner**

* 🌐 Portfolio: [https://www.dylanpicart.com](https://www.dylanpicart.com)
* 💼 LinkedIn: [https://linkedin.com/in/dylankpicart](https://linkedin.com/in/dylankpicart)
