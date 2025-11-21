# Real-Time School Climate — Databricks Transformation Layer

This directory contains the **Databricks compute and transformation logic** for the Real-Time School Climate Pipeline. It implements the **Silver** layer of the medallion architecture and securely loads curated data into **Snowflake Gold** for analytics.

The upstream **Bronze ingestion** is produced by Kafka → GCS Delta (via batch reseed or Dataproc streaming). This layer begins at Bronze and delivers **analysis-ready, enriched datasets** for district, borough, and school-level insights.

---

## **Directory Structure**

```text
rt_databricks/
│
├── utils/
│   ├── gcs_paths.py
│   ├── snowflake_options.py
│   └── __init__.py
│
├── bronze/
│   ├── 01_bronze_ingest.py
│   └── __init__.py
│
├── silver/
│   ├── 02_silver_school_climate.py
│   └── __init__.py
│
└── __init__.py
```

Each module is importable inside Databricks notebooks using the `Repos/` workspace Git integration.

---

## **Module Overview**

### 1. `utils/gcs_paths.py`

Canonical GCS path builder for all medallion layers.

Provides:

* `bronze_path(dataset)`
* `silver_path(dataset)`
* `checkpoint_path(stream_name)`

This ensures all raw, cleaned, and checkpoint data land under:

```bash
gs://rt-school-climate-delta/rt_school_climate/{bronze|silver|_checkpoints}
```

---

### 2. `utils/snowflake_options.py`

Secure Snowflake connector options for the Spark → Snowflake integration.

* Credentials fully sourced from the **Databricks secret scope `rt-school-climate`**
* No plaintext secrets anywhere
* Provides `get_sf_options()` returning:

  * `sfURL`
  * user, password
  * role, warehouse, database
  * schema (default: SILVER)

All writes to Snowflake use this module.

---

### 3. `bronze/bronze_ingest.py`

Kafka → Bronze Delta ingestion utilities.

Includes:

#### ● `build_confluent_kafka_options()`

Builds valid Confluent Cloud SASL_SSL configs using shaded JAAS:

```
kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule
```

#### ● `read_kafka_stream()`

Creates a raw streaming DataFrame from Kafka.

#### ● `build_bronze_df()`

Casts key/value to STRING
Adds `ingest_ts`
Preserves Kafka metadata.

#### ● `start_kafka_bronze_stream()`

Starts a Delta streaming sink into:

```python
bronze_path("school_climate_raw")
```

Works for classic Databricks compute.
For this pipeline, Bronze is seeded via batch pull or Dataproc streaming.

---

### 4. `silver/silver_school_climate.py`

The **core Silver transformation module**.

#### Responsibilities:

* Parse Bronze Kafka JSON payloads
* Flatten and clean fields
* Convert epoch → timestamps
* Time-stamp Silver loads
* Add **district_number** + **borough** derived from DBN
* Write curated Silver Delta to GCS
* Load Silver into Snowflake Silver schema
* Provide an orchestrated pipeline entrypoint

#### Major functions:

##### ● `get_bronze_value_schema()`

Schema tuned to real `value` JSON:

* `dbn`, `school_name`
* `total_parent_response_rate`
* `total_teacher_response_rate`
* `total_student_response_rate`
* NYC OpenData metadata fields (`:sid`, `:id`, `:created_at`, etc.)

##### ● `transform_bronze_to_silver(bronze_df)`

Produces Silver fields:

* `dbn`
* `school_name`
* `parent_response_rate`, `teacher_response_rate`, `student_response_rate`
* `district_number`, `borough`
* `created_at`, `updated_at`
* `event_ts`, `ingest_ts`, `load_ts`

##### ● `write_silver_to_snowflake(silver_df)`

Loads Silver → Snowflake:

```SQL
SCHOOL_CLIMATE.SILVER.SCHOOL_CLIMATE_CLEAN
```

##### ● `run_silver_pipeline(...)`

Full Bronze → Silver → Snowflake orchestration.

---

## **Medallion Architecture Summary**

### 🥇 Bronze (GCS Delta)

Kafka -> Delta
Raw unparsed JSON
Maintains all Kafka metadata

### 🥈 Silver (Databricks)

Flattened response rates
DBN → district/borough enrichment
Timestamps normalized
Schema-aligned for analytics
Delta table + Snowflake table

### 🥇 Gold (Snowflake)

Analytic views:

* `GOLD.SCHOOL_CLIMATE_SNAPSHOT`
* `GOLD.SCHOOL_CLIMATE_BOROUGH_SUMMARY`
* `GOLD.SCHOOL_CLIMATE_DISTRICT_SUMMARY`

Ready for Power BI ingestion.

---

## **Downstream Analytics (Power BI)**

Power BI connects to:

* `SCHOOL_CLIMATE.GOLD.SCHOOL_CLIMATE_SNAPSHOT`
* `SCHOOL_CLIMATE.GOLD.SCHOOL_CLIMATE_BOROUGH_SUMMARY`
* `SCHOOL_CLIMATE.GOLD.SCHOOL_CLIMATE_DISTRICT_SUMMARY`

Recommended visuals:

* Borough-level response patterns
* District comparison charts
* School-level scorecards
* Distribution of parent/teacher/student response rates

---

## **Testing**

### Bronze Test

Manual batch pull via:

```python
kafka_batch_df = spark.read.format("kafka").options(...).load()
```

### Silver Test

Use:

```python
import importlib
import rt_databricks.silver.silver_school_climate as ssc
importlib.reload(ssc)
ssc.run_silver_pipeline(...)
```

### Snowflake Test

```sql
SELECT * FROM SCHOOL_CLIMATE.SILVER.SCHOOL_CLIMATE_CLEAN LIMIT 50;
```

---

## **Deployment**

This package is ready for:

* Databricks Jobs
* Airflow DAGs calling notebooks/modules
* CI/CD via GitHub Actions
* Package versioning
* Unit/integration testing on Silver logic

---

## **Authors / Ownership**

This pipeline was engineered to modernize school climate analytics with:

* Real-time ingestion
* Modern medallion architecture
* Secure secret handling
* Cloud-native storage
* Snowflake analytical layers
* BI-ready schemas
