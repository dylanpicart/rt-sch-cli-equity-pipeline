# Real-Time Batch & Streaming ELT Pipeline

## Kafka · Databricks · Snowflake · dbt · Power BI · GCP

> **Project Status:** ~95% complete — dashboard live; Databricks Snowflake connector and job orchestration in final tuning.

This project is a **modern end-to-end ELT pipeline** that ingests both **streaming** and **batch** data to produce **clean, reliable, analytics-ready datasets** for citywide equity insights.
It demonstrates how Kafka, Databricks, dbt, and Snowflake come together in a **Medallion architecture (Bronze → Silver → Gold)** following industry best practices.

Built as part of the **Data Engineering Modern Toolkit** initiative.

---

## Purpose

Many organizations still depend on **manual spreadsheets and inconsistent data flows** to understand community or program outcomes.
This pipeline shows how to modernize those workflows using:

* **Streaming ingestion via Kafka**
* **Autoscaling distributed compute in Databricks**
* **Curated transformations with dbt + Snowflake**
* **Equity-focused analytics surfaced in Power BI**

The result is a **scalable, automated, reproducible** analytics stack.

---

## Architecture Overview

```text
Kafka (Streaming) ---> Bronze (Raw Landing) ---> Silver (Cleaned) ---> Gold (Curated Snowflake Models)
Batch Data ------^         |                         |                        |
Databricks (Spark Structured Streaming) + dbt (SQL models)
```

### Medallion Layers

* **Bronze:** Raw JSON/CSV from Kafka + supplemental batch reference data
* **Silver:** Cleaned, normalized, schema-validated Delta/Parquet
* **Gold:** dbt-modeled dimensional/tidy tables consumed directly by Power BI

A more detailed diagram is available in `/docs/project_overview.md`.

---

## Tech Stack

**Languages:** Python, SQL
**Streaming:** Apache Kafka (Confluent)
**Compute:** Databricks (Spark Structured Streaming)
**Storage:** Google Cloud Storage (Bronze/Silver)
**Warehouse:** Snowflake
**Transformation:** dbt
**Orchestration:** Databricks Workflows (in progress)
**Visualization:** Power BI
**DevOps:** GitHub, Makefile, isolated config environments

---

## Repository Structure

```text
rt-sch-cli-equity-pipeline/
│
├── README.md
├── .gitignore
│
├── jinja_templates/
│   ├── metric_query.sql.j2
│   ├── table_schema.sql.j2
│   ├── dbt_env_template.yml.j2
│   └── generate_sql.py
│
├── diagrams/
│   ├── architecture.png
│   └── medallion.png
│
├── data/
│   ├── svi_raw.csv
│   └── sample_climate_records.json
│
├── kafka/
│   ├── kafka_producer.py
│   ├── requirements.txt
│   └── config/
│       └── producer_config.json
│
├── databricks/
│   ├── streaming_notebook.py
│   ├── batch_svi_load.py
│   └── utils/
│       └── schema.py
│
├── dbt/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── bronze/
│   │   ├── silver/
│   │   └── gold/
│   ├── macros/
│   ├── tests/
│   └── seeds/
│
├── snowflake/
│   ├── create_tables.sql
│   ├── sample_queries.sql
│   └── sf_connector_example.py
│
├── powerbi/
│   ├── climate_vulnerability.pbix
│   └── exports/
│       ├── dashboard_screenshots/
│       └── metrics/
│
├── scripts/
│
└── screenshots/
    ├── kafka_topic.png
    ├── databricks_stream.png
    ├── snowflake_table.png
    └── dbt_lineage_graph.png
```

---

## Quick Start (Local Simulation)

> **Note:** This repo never includes real credentials or production configs.

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Copy example secrets

```bash
cp config/secrets.example.yml config/secrets.local.yml
```

### 3. Run local batch ingestion

```bash
python src/batch_ingestion/ingest_batch_reference.py
```

### 4. Run a mock streaming job

```bash
python src/streaming/streaming_job.py
```

---

## Databricks Integration (Real-Time Streaming)

Databricks is used exclusively for the **real-time streaming** side of the pipeline.
We use it to:

* **Ingest Kafka events into Bronze Delta tables** on GCS using Spark Structured Streaming
* **Transform Bronze → Silver** via Databricks notebooks and modular Python packages
* **Synchronize Silver → Snowflake Gold** tables using the native Snowflake connector
* **Manage secrets securely** using Databricks Secret Scopes (GCP Secret Manager–backed)

### Production-Ready Capabilities

* Autoscaling cluster configuration (DBR runtime, cluster policy, node sizing)
* Real-time **Kafka -> Bronze streaming job**
* **Bronze -> Silver** Delta Lake pipeline (schema cleaning, type normalization)
* **Silver -> Snowflake Gold** sync powering Power BI
* Notebook-driven and file-driven **Databricks Jobs** for orchestration

Progress documented in `/docs/project_overview.md`.

---

## Testing (Coming Soon)

Planned test suite:

* Schema validation tests
* Mock streaming tests
* dbt tests (unique, not-null, accepted values)
* UDF validation where applicable

---

## Roadmap

* [ ] Add full architecture diagram
* [ ] Add CI/CD workflow (linting + dbt tests)
* [ ] Integrate SVI into Power BI dashboard
* [ ] Docker development environment

---

## License

This project is licensed under the **MIT License**, which permits reuse, modification, distribution, and private or commercial use as long as the original license notice is included.

---

## Author

Developed by **Dylan Picart** at **Partnership With Children**.
**Portfolio:** [https://www.dylanpicart.com](https://www.dylanpicart.com)
**LinkedIn:** [https://linkedin.com/in/dylanpicart](https://linkedin.com/in/dylanpicart)
