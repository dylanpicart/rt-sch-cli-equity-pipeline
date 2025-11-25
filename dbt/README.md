# dbt Project – Gold Layer Modeling (Snowflake)

This directory contains the **dbt project** responsible for transforming Silver-layer climate and SVI data into curated **Gold analytical models** stored in Snowflake.
These models power the **NYC School Climate Dashboard** built in Power BI.

---

## Purpose

dbt is used in this pipeline to:

* Transform cleaned Silver-layer data into analytics-ready Gold tables
* Apply business logic and aggregations (school, district, borough)
* Ensure data quality through tests
* Document the semantic definitions of metrics
* Provide reproducible, version-controlled SQL models

Whereas Databricks handles **streaming** (Bronze → Silver), dbt handles **ELT inside Snowflake** (Silver → Gold).

---

## Project Structure

Typical structure inside `/dbt`:

```text
dbt/
│
├── models/
│   ├── school_climate/ (future work)
│   │   ├── snapshot.sql
│   │   ├── district_summary.sql
│   │   ├── borough_summary.sql
│   │
│   ├── svi/
│   │   ├── bronze/
│   │   ├── gold/
│   │   ├── silver/
|   |
│   ├── sources.yml
│   ├── schema.yml
│
├── profiles/ (optional override local)
├── dbt_project.yml
│
└── README.md
```

---

## How It Fits in the Pipeline

### Bronze & Silver (Databricks / Dataproc)

* Streaming climate data ingested via Kafka → Bronze Delta (Databricks)
* Cleaned using Databricks notebooks → Silver Delta
* Batch SVI data ingested via Dataproc Spark job

### Gold (dbt + Snowflake)

dbt connects to Snowflake using:

* A **SQL warehouse** or
* A **classic Snowflake connection** defined in `profiles.yml`

dbt then materializes:

* `SCHOOL_CLIMATE_SNAPSHOT`
* `SCHOOL_CLIMATE_DISTRICT_SUMMARY`
* `SCHOOL_CLIMATE_BOROUGH_SUMMARY`
* *(Future)* SVI Gold tables

These Gold tables serve as the backbone for **Power BI**.

---

## Running dbt

The Makefile already includes convenience commands, so dbt runs with:

```bash
make dbt-debug
make dbt-run
make dbt-test
```

Under the hood, this executes:

```bash
DBT_PROFILES_DIR=$(PWD)/.dbt dbt run
```

### Prerequisites

* Valid Snowflake credentials in `.dbt/profiles.yml`
* Warehouse + Role permissions
* Silver tables already loaded into Snowflake

---

## Testing (Data Quality)

Inside `schema.yml`, tests ensure:

* `dbn` is **unique** and **not null**
* Response rates are **within 0–1**
* Borough values match allowed categories
* District values are valid integers

Run tests:

```bash
make dbt-test
```

---

## Documentation (Optional but Recommended)

Generate dbt docs:

```bash
dbt docs generate
dbt docs serve
```

This will show:

* Lineage graph
* Model summaries
* Column-level documentation
* Tests and descriptions

Perfect for stakeholders and portfolio reviewers.

---

## Environment Configuration

Dbt profile lives in:

```text
dbt/.dbt/profiles.yml
```

It contains:

* `account` (Snowflake account ID)
* `user`
* `role`
* `warehouse`
* `database`
* `schema`
* `password` (recommended to load from `.env` instead)

Ensure `.dbt/` is **not committed** (it's in `.gitignore`).

---

## Future dbt Enhancements

Planned Gold models:

* `SVI_BY_DISTRICT`
* `SVI_BY_BOROUGH`
* School-level SVI integration
* Equity-weighted climate metrics
* Combined SVI + climate scorecards

These will expand the BI dashboard into a full equity analytics suite.
