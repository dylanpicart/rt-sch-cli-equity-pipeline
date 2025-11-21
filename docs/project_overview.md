# Project Overview

## Real-Time Batch & Streaming Data Pipeline (Kafka → Databricks → Snowflake → dbt → Power BI)

This document provides a deeper architectural breakdown of the project—covering design reasoning, scalability considerations, and implementation details across the full medallion architecture.

---

## 1. Goals

This project demonstrates how to build a **production-grade medallion architecture** that unifies:

* **Streaming ingestion** (Kafka → Bronze)
* **Batch ingestion** (reference datasets)
* **Distributed compute** (Spark on Databricks)
* **Analytics modeling** (dbt)
* **Cloud warehousing** (Snowflake)
* **BI-ready visualizations** (Power BI)

The broader goal: show how modern Data Engineers design pipelines that are:

* **Reliable** — schema-enforced, validated, replayable
* **Scalable** — autoscaling compute, partition-aware storage
* **Testable** — dbt tests, Pytest (planned)
* **Secure** — secret-scoped Snowflake + Kafka configs
* **Observable** — lineage and monitoring planned (OpenLineage, Prometheus)

---

## 2. Core Architecture

```text
     ┌───────────────────────┐
     │       Kafka Topic      │
     │   (streaming events)   │
     └─────────────┬─────────┘
                   │ Spark Structured Streaming
                   ▼
              ┌──────────┐
              │  Bronze  │  (Raw layer in GCS)
              └────┬─────┘
              ETL / cleanup in Databricks
                   ▼
              ┌──────────┐
              │  Silver  │  (Cleaned, normalized)
              └────┬─────┘
                 dbt transformations
                   ▼
              ┌──────────┐
              │   Gold   │  (Curated Snowflake models)
              └────┬─────┘
                   ▼
              Power BI Dashboards
```

---

## 3. Layer Breakdown

### **Bronze Layer — Raw Landing (GCS)**

Stores raw data exactly as received. Includes:

* **Streaming data:** Kafka → Databricks → GCS
* **Batch data:** Uploaded reference CSV/Parquet files

Purpose:

* Preserve original fidelity
* Allow schema-on-read
* Support backfills/reprocessing
* Enable time-travel & debugging

---

### **Silver Layer — Cleaned & Normalized**

Processed in Databricks with Spark:

* Enforces schemas
* Deduplicates and handles late-arriving events
* Applies normalization (date formats, field standardization)
* Writes Delta/Parquet
* Partitions by `event_date` / `school_id` for performance

Outcome: **stable, query-ready datasets**.

---

### **Gold Layer — Curated Analytics Models (Snowflake via dbt)**

dbt models power the curated Snowflake schema:

* **Dimensions:** `dim_school`, `dim_borough`, `dim_language`, etc.
* **Facts:** `fact_equity_metrics`, `fact_climate_scores`, etc.
* **Optional:** SCD2 snapshots for slowly changing dimensions

dbt tests include:

* `unique`
* `not_null`
* `accepted_values`
* referential integrity

These feed directly into the **Power BI dashboard**, now live.

---

## 4. Databricks Configuration (Nearing Completion)

### Cluster configuration (current)

* **DBR Runtime:** 13.x LTS
* **Worker Autoscaling:** min 1 → max 4
* **Instance type:** GCP compute-optimized equivalent
* **Mode:**

  * *Single-Node* for prototyping
  * *Autoscaling Standard Cluster* for streaming
* **Libraries Installed:**

  * `pyspark`
  * `delta-spark`
  * Kafka connector
  * Snowflake connector

### Workflows (planned)

* dbt Cloud Transformation Job
* Databricks Job Runner for dbt Core + Snowflake sync

All Databricks -> Snowflake credentials use **secret scopes**, not plaintext.

---

## 5. Snowflake Modeling

dbt drives the transformation layer.

### Model Structure

```text
dbt/
├── models/
│   ├── staging/
│   │   ├── stg_stream_events.sql
│   │   └── stg_reference_data.sql
│   ├── marts/
│   │   ├── fact_equity_metrics.sql
│   │   └── dim_school.sql
│   └── snapshots/
│       └── school_snapshot.sql
```

Key patterns:

* **Staging models:** Clean + standardize
* **Marts:** Metric aggregation + joins
* **Snapshots:** Historical comparison and SCD2

---

## 6. Testing Strategy

### dbt Tests (active)

* Schema: `unique`, `not_null`
* Domain: `accepted_values`
* Foreign keys: `relationships`

### Pytest (coming)

* Schema validation for micro-batches
* Batch ingestion tests
* End-to-end ingestion → transformation checks

### Future Quality Enhancements

* Great Expectations or Soda
* Unit tests for Kafka → Bronze ingestion

---

## 7. Power BI Layer

The Power BI dashboard is now **fully functional**, showing:

* Borough- and school-level equity metrics
* SVI (vulnerability) indicators
* Climate snapshot performance
* District comparisons
* Downloadable drillthroughs
* Combined batch + streaming insights

Screenshots available under `powerbi/exports/`.

---

## 8. Future Enhancements

* Add Docker development environment
* Add CI/CD (GitHub Actions) for:

  * linting
  * dbt tests
  * documentation builds
* Add Great Expectations or Soda for data quality
* Add OpenLineage for table & job lineage
* Add Prometheus/Grafana for streaming pipeline observability
* Add Power BI dataset refresh automation

---

## 9. Author

**Dylan Picart**
Data Engineering · Cloud · Streaming · Analytics
Portfolio: [https://www.dylanpicart.com](https://www.dylanpicart.com)
LinkedIn: [https://linkedin.com/in/dylanpicart](https://linkedin.com/in/dylanpicart)
