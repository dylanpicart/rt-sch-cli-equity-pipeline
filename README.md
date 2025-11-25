# **Real-Time Batch & Streaming ELT Pipeline**

[![CI Status](https://github.com/dylanpicart/rt-sch-cli-equity-pipeline/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/dylanpicart/rt-sch-cli-equity-pipeline/actions/workflows/ci.yml)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue)
![dbt](https://img.shields.io/badge/dbt-Core%201.1x-blue)
![Terraform](https://img.shields.io/badge/Terraform-IaC-purple)
![MIT License](https://img.shields.io/badge/license-MIT-green)

## **Kafka · Databricks · Snowflake · dbt · Power BI · GCP · Terraform · CI/CD**

> **Project Status:** Production-ready.
> Full CI/CD + IaC + DevSecOps pipeline implemented.
> Dashboard live; Databricks Snowflake connector and job orchestration finalized.

This project is a **modern, end-to-end ELT platform** combining streaming, batch, distributed compute, cloud warehousing, and automated transformations.
It demonstrates how **Kafka, Databricks, dbt, and Snowflake** integrate in a **Medallion Architecture (Bronze → Silver → Gold)** to support **equity-focused analytics** across NYC school climate datasets.

Built as part of the **Data Engineering Modern Toolkit** initiative.

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
                ┌───────────────────────────┐
                │          Kafka            │
                │   (Real-time Streaming)   │
                └──────────────┬────────────┘
                               ▼
                        Bronze (Raw)
                      GCS Landing Zone
                               ▼
        ┌───────────────────────────────┐
        │  Databricks (Spark Structured │
        │       Streaming + Batch)      │
        └───────────────────────────────┘
                               ▼
                        Silver (Cleaned)
                     Delta / Parquet / GCS
                               ▼
                 dbt → Snowflake (Gold Models)
                               ▼
                   Power BI (Equity Dashboard)
```

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
**Orchestration** – Databricks Jobs
**Visualization** – Power BI
**DevOps** – Terraform, GitHub Actions, Makefile, pre-commit, detect-secrets

---

## Repository Structure

```text
root/
│
├── README.md
├── SECURITY.md
├── .gitignore
│
├── infra/
│   └── terraform/
│       ├── providers.tf
│       ├── variables.tf
│       ├── gcs.tf
│       ├── snowflake.tf
│       ├── databricks.tf
│       ├── dataproc.tf
│       ├── gcp_snowflake_integration.tf
│       ├── main.tf
│       ├── terraform.tfvars.example
│       └── terraform.dev.tfvars (ignored)
│
├── dbt/
│   ├── models/
│   │   ├── bronze/
│   │   ├── silver/
│   │   └── gold/
│   ├── macros/
│   ├── tests/
│   └── seeds/
│
├── databricks/
│   ├── bronze_to_silver_notebook.py
│   ├── streaming/
│   └── utils/
│
├── kafka/
│   ├── kafka_producer.py
│   └── config/
│
├── scripts/
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

* [ ] Add detailed table-level lineage diagram (Bronze → Silver → Gold, SVI + Climate models)
* [ ] Add automated integration test suite (end-to-end tests hitting dev Snowflake / GCS)
* [ ] Add Databricks Jobs API orchestration (trigger + monitor jobs via REST/SDK)
* [ ] Add Docker local environment for reproducible dev + CI
* [ ] Add Power BI refresh automation (triggered after successful ELT runs)
* [ ] Integrate SVI dashboard and merge SVI data with School Climate data for cross-referenced equity analysis

---

## License

MIT License — free for personal and commercial use.

---

## Author

**Dylan Picart**
Data Engineer & Analytics Engineer

* 🌐 Portfolio: [https://www.dylanpicart.com](https://www.dylanpicart.com)
* 💼 LinkedIn: [https://linkedin.com/in/dylanpicart](https://linkedin.com/in/dylanpicart)
