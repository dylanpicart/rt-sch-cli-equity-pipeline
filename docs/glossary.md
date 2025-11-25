# Glossary of Terms – NYC School Climate Pipeline

**Bronze Layer**
The raw ingestion layer of the medallion architecture. Stores unprocessed Kafka events with full metadata and original JSON payloads.

**Silver Layer**
Cleansed, typed, and normalized data. Handles schema correction, deduplication, data quality adjustments, and enrichment.

**Gold Layer**
Analytics-ready tables. Aggregated by school, district, and borough. Used directly by Power BI and downstream analytics.

**DBN (District Borough Number)**
A unique identifier for NYC public schools. First two digits represent the school district; the third letter represents the borough.

**SVI (Social Vulnerability Index)**
A CDC metric representing community vulnerability based on socioeconomic, demographic, and housing characteristics.

**RPL Themes (1–4)**
Four underlying components of SVI:

1. Socioeconomic status
2. Household composition & disability
3. Minority status & language
4. Housing & transportation access

**Databricks**
A unified Spark-based analytics platform used here for real-time streaming (Kafka -> Delta) and Bronze/Silver transformations.

**Spark Structured Streaming**
A scalable, fault-tolerant, micro-batch and continuous-processing streaming engine built on Apache Spark. It provides high-level, declarative streaming APIs using the same DataFrame and SQL abstractions used for batch processing.

**Snowflake**
A cloud-based data warehouse used to store, model, and serve Gold-layer analytics tables.

**Dataproc**
Google Cloud’s managed Spark/Hadoop service used for batch ingestion (CDC SVI).

**Delta Lake**
ACID-compliant storage format used on GCS for Bronze/Silver layers.

**dbt**
A SQL transformation framework used to build, document, and test Snowflake Gold models.

**Power BI**
The business intelligence tool used for interactive dashboards and visual exploration.

**Confluent Kafka**
The streaming ingestion backbone for real-time climate survey events.

**Medallion Architecture**
A data modeling pattern consisting of Bronze (raw), Silver (clean), and Gold (analytics) layers.
