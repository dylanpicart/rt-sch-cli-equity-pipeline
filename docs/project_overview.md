# Project Overview  
## Real-Time Batch & Streaming Data Pipeline (Kafka → Databricks → Snowflake → dbt)

This document provides a deeper architectural breakdown of the project, including reasoning behind design choices, scalability considerations, and implementation details.

---

# 1. Goals

This project demonstrates how to build a **production-grade medallion architecture** that harmonizes:

- **Streaming** (Kafka → Bronze)
- **Batch ingestion** (reference datasets)
- **Distributed transformations** (Databricks / Spark)
- **Analytics modeling** (dbt)
- **Cloud data warehousing** (Snowflake)
- **BI-ready outputs** (Power BI)

The goal is to illustrate how a modern Data Engineer designs pipelines that are:

- **Reliable**
- **Scalable**
- **Testable**
- **Secure**
- **Observability-friendly**

---

# 2. Core Architecture

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

# 3. Layer Breakdown

## **Bronze Layer (Raw Landing Zone)**  
Stores raw data exactly as received:

- **Streaming data:** Kafka → Databricks streaming → GCS raw zone  
- **Batch data:** Uploaded Parquet/CSV reference files  

Purpose:
- Retain original fidelity  
- Allow schema-on-read  
- Support replay and backfill  

---

## **Silver Layer (Cleaned & Normalized)**

Spark in Databricks:

- Enforces schema  
- Handles late-arriving data  
- Deduplicates  
- Converts files to Parquet/Delta  
- Applies partitioning strategy (e.g., by date or school_id)

This layer creates **stable, analytics-friendly tables**.

---

## **Gold Layer (Curated Analytics Models)**

dbt in Snowflake:

- Dimension tables: `dim_school`, `dim_borough`, etc.  
- Fact tables: `fact_event_metrics`, `fact_equity_scores`  
- Snapshot logic for SCD2 (if needed)  
- Tests:
  - unique
  - not null
  - accepted values
  - referential integrity  

Outputs feed Power BI dashboards.

---

# 4. Databricks Configuration (In Progress)

## Planned configuration:
- **DBR Runtime:** 13.x LTS  
- **Workers:** Autoscaling (min 1, max 4)  
- **Instance type:** `i3.xlarge` or GCP equivalent (for streaming)  
- **Cluster mode:** Standard or Single-Node for development  
- Libraries:
  - `pyspark`
  - `delta`
  - `databricks-kafka` connector  

## Jobs planned:
1. `kafka_to_bronze_streaming_job`  
2. `bronze_to_silver_job`  
3. `silver_to_snowflake_job`  
4. `dbt_transformations_job`

---

# 5. Snowflake Modeling

dbt handles the transformations:

### Example model structure:

```

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

---

# 6. Testing Strategy

## dbt Tests
- Schema tests (unique, not_null)  
- Custom tests (e.g., valid borough names)  

## Pytest (planned)
- Schema validation for streaming micro-batches  
- Batch ingestion integrity tests  

---

# 7. Power BI Layer

The Power BI dashboard (planned):

- Equity metrics  
- School or district-level breakdowns  
- Streaming vs batch comparisons  
- Historical trends  

---

# 8. Future Enhancements

- Add Docker development environment  
- Add Great Expectations / Soda for data quality  
- Add end-to-end CI/CD (GitHub Actions)  
- Add lineage with OpenLineage  
- Add monitoring with Databricks metrics + Prometheus  

---

# 9. Author

**Dylan Picart**  
Data Engineering · Cloud · Streaming · Analytics  
Portfolio: https://www.dylanpicart.com  
LinkedIn: https://linkedin.com/in/dylanpicart