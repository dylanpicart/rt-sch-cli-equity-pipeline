# Databricks subproject

This `databricks/` directory contains the Databricks-side implementation
of the **rt-sch-cli-equity-pipeline** project.

## Layout

- `bronze/`: Kafka -> Delta Bronze streaming job(s)
- `silver/`: cleaning & conforming logic for Silver Delta tables
- `snowflake/`: loaders that push Silver tables into Snowflake
- `utils/`: shared schema, config, GCS paths, Snowflake options
- `configs/`: external config files (if needed later)
- `workflows/`: JSON/YAML job definitions for Databricks Jobs
- `notebooks/`: ad hoc Databricks notebooks
- `dbt/`: hooks/helpers related to the dbt project in the repo root
