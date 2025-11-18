# Snowflake / dbt Models

This directory contains the **Gold-layer transformations** for the data pipeline, implemented using **dbt** and executed against **Snowflake**. These models represent the final curated dataset used for analytics, reporting, and downstream applications such as Power BI dashboards.

The Snowflake layer acts as the authoritative source of truth for clean, validated, and analytics-ready tables derived from both streaming and batch data ingested through Kafka, Databricks, and GCP.

---

## Purpose of This Layer

The Snowflake/dbt layer serves three core functions:

1. **Transform raw and cleaned data into dimensional models**  
   - Fact tables for event-level and time-series metrics  
   - Dimension tables for schools, districts, demographics, or reference entities  

2. **Apply data quality checks and constraints**  
   - dbt tests guarantee schema consistency, uniqueness, referential integrity, and value ranges  

3. **Provide a stable and documented interface**  
   - Downstream BI tools and analysts consume vetted models instead of raw or semi-structured data  

---

## Structure

```text
dbt/
├── models/
│   ├── staging/
│   │   ├── stg_stream_events.sql
│   │   ├── stg_batch_reference.sql
│   │   └── stg_common_fields.sql
│   ├── marts/
│   │   ├── fact_equity_metrics.sql
│   │   ├── dim_school.sql
│   │   └── dim_date.sql
│   ├── snapshots/
│   │   └── school_snapshot.sql
│   └── schema.yml
├── macros/
│   └── utility_macros.sql
├── seeds/
│   └── reference_tables.csv
└── dbt_project.yml
```

---

## Model Layers

### Staging Layer (`models/staging/`)

The staging layer standardizes and lightly transforms inputs from Bronze and Silver tables.  
Key responsibilities:

- Column renaming  
- Data type enforcement  
- Removing nested structures or arrays  
- Basic normalization such as trimming or lowercasing  

These models are designed to be thin and purely structural.

### Marts Layer (`models/marts/`)

The marts layer contains the business-ready tables used by dashboards and applications.  
Examples:

- `fact_equity_metrics` combines processed streaming data with reference attributes  
- `dim_school` creates a master lookup table used across all analytics  
- `dim_date` standardizes date-based metrics, joins, and aggregations  

This layer follows a dimensional modeling approach (fact and dimension tables).

### Snapshots (`snapshots/`)

Snapshots track changes to slowly changing dimensions (SCD2).  
Typical uses:

- Tracking school attribute changes over time  
- Preserving historical versions for auditing or backfill operations  

### Seeds (`seeds/`)

Seeds store static reference data, version-controlled and deployed directly into Snowflake.  
Examples:

- Borough mappings  
- Classification codes  
- Benchmark thresholds  

---

## dbt Tests and Quality Assurance

The project uses both built-in and custom dbt tests.

Built-in tests:

- `unique`  
- `not_null`  
- `accepted_values`  
- `relationships`  

Custom tests (optional):

- Ensuring only valid borough names are used  
- Ensuring metrics fall within defined numeric ranges  
- Enforcing referential integrity between facts and dimensions  

Running tests:

```bash
dbt test
````

---

## Running the Project

All dbt commands must be executed from within the `dbt/` directory after configuring a `profiles.yml` file on your local machine.

Typical workflow:

```bash
dbt deps
dbt seed
dbt run
dbt test
```

If using Snowflake:

* Ensure your profile uses an environment-specific connection
* Do not commit credentials or private key files to the repository

---

## Environments and Naming Conventions

The project follows a standard environment pattern:

* `dev`
* `test`
* `prod`

Object naming conventions:

* Lowercase snake_case
* Prefix `stg_` for staging
* Prefix `fact_` and `dim_` for marts
* Prefix `snap_` for snapshots

---

## Integration with Upstream Layers

Upstream:

* Silver Delta tables produced by Databricks provide cleaned event and reference data

Downstream:

* Power BI dashboards
* Program evaluation metrics
* Equity analytics, trend analysis, and reporting tools

Snowflake acts as the unified, stable interface for all consumer layers.

---

## Future Improvements

* Add column-level lineage via dbt docs and OpenLineage
* Add incremental materializations for fact tables
* Add automated schema drift detection
* Add unit tests for custom macros
* Add continuous deployment via GitHub Actions

---

## Notes

This directory does not contain:

* Snowflake credentials
* Tokens, passwords, private keys
* Environment-specific config values

All sensitive information should be provided through `profiles.yml` or environment variables on the developer's machine.

---
