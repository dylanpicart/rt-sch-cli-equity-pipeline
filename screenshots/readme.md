# Screenshots Overview

This folder contains visual evidence of the full, multiplatform workflow implemented in the **RT School Climate Equity Pipeline**.
Each screenshot highlights a key stage of the architecture across **GCP, Databricks, Snowflake, dbt, and downstream analytics**.

## Included Screenshots

### 1. Databricks — Silver Transformation Test

**File:** `Databricks_Silver_Test.png`
Shows Databricks notebooks used to clean, enforce schema, and build the Silver climate tables using Spark Structured Streaming and Autoloader.

### 2. GCS — Bucket Structure

**File:** `GCP_Bucket_Directory_Structure.png`
Displays the layout of the GCS bucket hosting `bronze/` and `silver/` Delta/Parquet layers for both streaming (climate) and batch (SVI) pipelines.

### 3. Snowflake — Gold Climate Tables

**File:** `Snowflake_DB_Gold_Climate.png`
Demonstrates Snowflake SQL logic, dbt-generated models, and the resulting Gold tables (borough-, district-, and school-level equity metrics). Includes query results and visual distributions.

### 4 RAG Service — Lightweight Semantic Q&A UI

**File:** `Lightweight_RAG_UI.png`
Showcases the React/Vite TypeScript interface built for the School Climate & SVI RAG (Retrieval-Augmented Generation) Service. UI sends structured queries to the FastAPI backend, which combines:

Dynamic Environment Labels:
The UI displays real-time backend status (REAL / FAKE) using /api/status
and a frontend development flag (VITE_FAKE_MODE), making it easy to test locally without burning tokens.

Human-Readable Equity Insights:
The LLM synthesizes SVI themes with climate survey domains (safety, relationships, engagement)
into:

## Purpose

These screenshots serve as:

- **Proof of correct platform integration** across GCP → Databricks → Snowflake.
- **Verification of medallion architecture** (Bronze → Silver → Gold).
- **Evidence of operational workflows**, schema validations, and final analytical outputs.
- Provides leadership-friendly equity insights grounded in dbt-validated data
- RAG runs in both production (real LLM) and offline (fake LLM + fake embeddings) modes
- **Portfolio-ready snapshots** showing end-to-end data engineering work.

## Directory Structure

```text
screenshots/
├── Databricks_Silver_Test.png
├── GCP_Bucket_Directory_Structure.png
├── Snowflake_DB_Gold_Climate.png
├── Lightweight_RAG_UI.png
└── README.md```
