# rt-sch-cli-equity-pipeline/Makefile

PYTHON ?= python

# dbt command with project-local profiles directory
DBT := DBT_PROFILES_DIR=$(PWD)/.dbt dbt

# ---------------------------------------------------------
# Load local environment variables from .env (if present)
# ---------------------------------------------------------
ifneq (,$(wildcard .env))
    include .env
    # Export all non-comment variable names from .env
    export $(shell sed -n 's/^\([^#][^=]*\)=.*/\1/p' .env)
endif

# ---------------------------------------------------------
# GCS bucket for this project
# Prefer GCP_BUCKET_NAME from .env, fallback to explicit name
# ---------------------------------------------------------
ifdef GCP_BUCKET_NAME
    BUCKET := $(GCP_BUCKET_NAME)
else
    BUCKET := rt-school-climate-delta
endif

# Default object paths
SVI_OBJECT      ?= raw/svi/cdc_svi_ny_2022.csv
CLIMATE_OBJECT  ?= raw/climate/nyc_school_climate_raw.json

# Data source URLs (override in env if they ever change)
SVI_CSV_URL    ?= https://svi.cdc.gov/Documents/Data/2022/csv/states/NewYork.csv
CLIMATE_API_URL ?= https://data.cityofnewyork.us/api/views/fb6n-h22r/rows.json?accessType=DOWNLOAD

# Dataproc & Snowflake job settings
DP_CLUSTER_NAME ?= rt-school-climate-cluster
DP_REGION       ?= us-east1
DP_ZONE         ?= us-east1-b

JARS_LOCAL_DIR  ?= jars
JARS_GCS_URI    ?= gs://$(BUCKET)/jars

SPARK_SF_JAR    ?= spark-snowflake_2.12-2.16.0-spark_3.3.jar
SF_JDBC_JAR     ?= snowflake-jdbc-3.19.0.jar

SF_PROPS_FILE   ?= .secrets/spark_snowflake.properties

# ---------------------------------------------------------

.PHONY: help fetch-svi fetch-climate fetch-data data-dirs \
        dataproc-create-cluster dataproc-delete-cluster \
        upload-snowflake-jars load-svi-snowflake \
        load-svi-snowflake-alt \
        dbt-debug dbt-run dbt-test

help:
	@echo "Available targets:"
	@echo "  make data-dirs               - Create local data/ folder structure"
	@echo "  make fetch-svi               - Download CDC SVI NY 2022 CSV and upload to GCS"
	@echo "  make fetch-climate           - Download NYC School Climate JSON and upload to GCS"
	@echo "  make fetch-data              - Run both fetch-svi and fetch-climate"
	@echo "  make dataproc-create-cluster - Create single-node Dataproc cluster"
	@echo "  make dataproc-delete-cluster - Delete Dataproc cluster"
	@echo "  make upload-snowflake-jars   - Upload Snowflake connector JARs to GCS"
	@echo "  make load-svi-snowflake      - Run Dataproc Spark job to load SVI into Snowflake"
	@echo "  make load-svi-snowflake-alt  - Load SVI into Snowflake via local Python fallback"
	@echo "  make dbt-debug               - Run 'dbt debug' with project-local profiles"
	@echo "  make dbt-run                 - Run 'dbt run' with project-local profiles"
	@echo "  make dbt-test                - Run 'dbt test' with project-local profiles"

data-dirs:
	mkdir -p data/source_svi/raw
	mkdir -p data/source_svi/docs
	mkdir -p data/source_svi/samples
	mkdir -p data/source_climate/raw
	mkdir -p data/source_climate/docs
	mkdir -p data/source_climate/samples
	mkdir -p data/processed

fetch-svi:
	@echo ">>> Fetching CDC SVI NY 2022 CSV and uploading to GCS..."
	$(PYTHON) scripts/gcp/fetch_svi_to_gcs.py \
		--url "$(SVI_CSV_URL)" \
		--bucket "$(BUCKET)" \
		--object "$(SVI_OBJECT)"

fetch-climate:
	@echo ">>> Fetching NYC School Climate JSON and uploading to GCS..."
	$(PYTHON) scripts/gcp/fetch_climate_to_gcs.py \
		--url "$(CLIMATE_API_URL)" \
		--bucket "$(BUCKET)" \
		--object "$(CLIMATE_OBJECT)"

fetch-data: fetch-svi fetch-climate
	@echo ">>> All data sources fetched and uploaded."

dataproc-create-cluster:
	@echo ">>> Creating Dataproc cluster $(DP_CLUSTER_NAME) in $(DP_REGION)..."
	gcloud dataproc clusters create $(DP_CLUSTER_NAME) \
	  --region=$(DP_REGION) \
	  --zone=$(DP_ZONE) \
	  --single-node \
	  --master-machine-type=n1-standard-4 \
	  --master-boot-disk-size=100GB \
	  --image-version=2.2-debian12

dataproc-delete-cluster:
	@echo ">>> Deleting Dataproc cluster $(DP_CLUSTER_NAME) in $(DP_REGION)..."
	gcloud dataproc clusters delete $(DP_CLUSTER_NAME) \
	  --region=$(DP_REGION) \
	  --quiet

upload-snowflake-jars:
	@echo ">>> Uploading Snowflake connector JARs to $(JARS_GCS_URI)..."
	gsutil cp $(JARS_LOCAL_DIR)/$(SPARK_SF_JAR) $(JARS_GCS_URI)/
	gsutil cp $(JARS_LOCAL_DIR)/$(SF_JDBC_JAR) $(JARS_GCS_URI)/

load-svi-snowflake: upload-snowflake-jars
	@echo ">>> Submitting Dataproc job to load SVI into Snowflake..."
	gcloud dataproc jobs submit pyspark \
	  dataproc/jobs/load_svi_to_snowflake.py \
	  --cluster=$(DP_CLUSTER_NAME) \
	  --region=$(DP_REGION) \
	  --jars=$(JARS_GCS_URI)/$(SPARK_SF_JAR),$(JARS_GCS_URI)/$(SF_JDBC_JAR) \
	  --properties-file=$(SF_PROPS_FILE)

load-svi-snowflake-alt:
	@echo ">>> Loading SVI from GCS into Snowflake using local Python (alt loader)..."
	$(PYTHON) scripts/snowflake/alt_load_svi_to_snowflake.py

dbt-debug:
	cd dbt && $(DBT) debug

dbt-run:
	cd dbt && $(DBT) run

dbt-test:
	cd dbt && $(DBT) test
