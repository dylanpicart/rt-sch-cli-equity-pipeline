# Real-Time Batch & Streaming ELT Pipeline  
### Kafka · Databricks · Snowflake · dbt · Power BI · GCP

> *Project Status:* ~85% complete — Databricks cluster configuration and job orchestration currently being finalized.

This project is a **modern end-to-end data engineering ELT pipeline** that ingests both **streaming** and **batch** data to produce **clean, reliable, analytics-ready datasets** for equity insights. It demonstrates how to combine Kafka, Databricks, dbt, and Snowflake within a Medallion architecture (Bronze → Silver → Gold) following industry best practices.

---

## Purpose

Many organizations rely on fragmented spreadsheets and manual workflows to understand community or program data. This pipeline shows how to modernize that process with:

- **Streaming ingestion (Kafka)**
- **Distributed compute (Databricks / Spark Structured Streaming)**
- **Curated transformations (dbt + Snowflake)**
- **Equity-focused analytics (Power BI)**

It is built as part of a broader **Data Engineering Modern Toolkit** initiative.

---

## Architecture at a Glance

```text
Kafka (Streaming) ---> Bronze (Raw Landing) ---> Silver (Cleaned) ---> Gold (Curated Models in Snowflake)
Batch Data ------^         |                         |                        |
Databricks / Spark Structured Streaming + dbt Transforms
```

### Key Concepts

- **Bronze:** Raw JSON/CSV from Kafka + batch reference tables  
- **Silver:** Cleaned, normalized, schema-enforced Delta/Parquet  
- **Gold:** dbt-modeled dimensional tables for BI  

A more detailed diagram can be found in `/docs/project_overview.md`.

---

## Tech Stack

**Languages:** Python, SQL  
**Streaming:** Apache Kafka  
**Compute:** Databricks (Spark Structured Streaming)  
**Storage:** Google Cloud Storage (Bronze / Silver)  
**Warehouse:** Snowflake  
**Transformation:** dbt  
**Orchestration (Planned):** Databricks Jobs  
**Visualization:** Power BI  
**DevOps:** Git, Makefile, environment-isolated configs  

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
│       └── dashboard_screenshots/
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

> **NOTE:** *This repository never includes real credentials or production configs.*

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

## Databricks Integration (In Progress)

Work remaining:

* Cluster config (autoscaling, DBR runtime, network settings)
* Kafka → Bronze streaming job
* Bronze → Silver Delta conversion
* Silver → Snowflake Gold sync
* Job orchestration via Databricks Workflows

Progress will be reflected in `/docs/project_overview.md`.

---

## Testing (Coming Soon)

Unit tests for:

* Schema validation
* Streaming transformations
* dbt test suite (unique, not-null, accepted values)

---

## Roadmap

* [ ] Finalize Databricks cluster + job configuration
* [ ] Add full architecture diagram
* [ ] Add CI/CD workflow (lint + dbt tests)
* [ ] Add example Power BI dashboard
* [ ] Add Docker development environment

---

## License

MIT

---

## Contact

**Author:** Dylan Picart
**Portfolio:** https://www.dylanpicart.com
**LinkedIn:** https://linkedin.com/in/dylanpicart
