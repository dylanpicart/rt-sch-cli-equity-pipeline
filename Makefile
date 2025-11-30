# =========================================================
# rt-sch-cli-equity-pipeline / Makefile
# =========================================================

PYTHON ?= python

# dbt command with project-local profiles directory
DBT := DBT_PROFILES_DIR=$(PWD)/.dbt dbt

# =========================================================
# Load local environment variables from .env (if present)
# =========================================================
ifneq (,$(wildcard .env))
    include .env
    export $(shell sed -n 's/^\([^#][^=]*\)=.*/\1/p' .env)
endif

# =========================================================
# GCS bucket configuration
# =========================================================
ifdef GCP_BUCKET_NAME
    BUCKET := $(GCP_BUCKET_NAME)
else
    BUCKET := actual-hardcoded-bucket-name
endif

SVI_OBJECT       ?= raw/svi/cdc_svi_ny_2022.csv
CLIMATE_OBJECT   ?= raw/climate/nyc_school_climate_raw.json
SVI_CSV_URL      ?= https://svi.cdc.gov/Documents/Data/2022/csv/states/NewYork.csv
CLIMATE_API_URL  ?= https://data.cityofnewyork.us/api/views/fb6n-h22r/rows.json?accessType=DOWNLOAD

# Dataproc cluster config
DP_CLUSTER_NAME ?= ${GCP_DATAPROC_CLUSTER_NAME}
DP_REGION       ?= ${GCP_REGION}
DP_ZONE         ?= ${GCP_ZONE}

# JARS
JARS_LOCAL_DIR  ?= jars
JARS_GCS_URI    ?= gs://$(BUCKET)/jars
SPARK_SF_JAR    ?= spark-snowflake_2.12-2.16.0-spark_3.3.jar
SF_JDBC_JAR     ?= snowflake-jdbc-3.19.0.jar
SF_PROPS_FILE   ?= .secrets/spark_snowflake.properties

# =========================================================
# Terraform configuration
# =========================================================
TERRAFORM_DIR := infra/terraform

infra-init:
	@echo ">>> Initializing Terraform..."
	cd $(TERRAFORM_DIR) && terraform init

infra-plan:
	@echo ">>> Terraform plan..."
	cd $(TERRAFORM_DIR) && terraform plan -var-file="terraform.tfvars"

infra-up:
	@echo ">>> Applying Terraform (creating infra)..."
	cd $(TERRAFORM_DIR) && terraform apply -var-file="terraform.tfvars" -auto-approve

infra-down:
	@echo ">>> Destroying Terraform-managed infra..."
	cd $(TERRAFORM_DIR) && terraform destroy -var-file="terraform.tfvars" -auto-approve

infra-fmt:
	@echo ">>> Formatting Terraform..."
	cd $(TERRAFORM_DIR) && terraform fmt

# =========================================================
# Python Quality: Linting + Formatting + Testing
# =========================================================
lint:
	@echo ">>> Running Ruff..."
	ruff check . --exclude='.venv' --exclude='dbt/target' --exclude='.dbt'
	@echo ">>> Running Flake8..."
	flake8 . --exclude=.venv,dbt/target,.dbt
	@echo ">>> Running Black (--check)..."
	black . --check --exclude '(\.venv|dbt/target|\.dbt)'

format:
	@echo ">>> Running Black (formatting)..."
	black . --exclude '(\.venv|dbt/target|\.dbt)'

test:
	@echo ">>> Running unit + integration tests..."
	pytest -q

# =========================================================
# Data Acquisition
# =========================================================
.PHONY: data-dirs fetch-svi fetch-climate fetch-data

data-dirs:
	mkdir -p data/source_svi/raw
	mkdir -p data/source_svi/docs
	mkdir -p data/source_svi/samples
	mkdir -p data/source_climate/raw
	mkdir-p data/source_climate/docs
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

# =========================================================
# Dataproc Jobs
# =========================================================
.PHONY: dataproc-create-cluster dataproc-delete-cluster \
        upload-snowflake-jars load-svi-snowflake load-svi-snowflake-alt

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
	@echo ">>> Loading SVI from GCS into Snowflake (local fallback)..."
	$(PYTHON) scripts/snowflake/alt_load_svi_to_snowflake.py

# =========================================================
# dbt Commands
# =========================================================
.PHONY: dbt-debug dbt-run dbt-test

dbt-debug:
	cd dbt && $(DBT) debug

dbt-run:
	cd dbt && $(DBT) run

dbt-test:
	cd dbt && $(DBT) test

	# =========================================================
# RAG Service (Backend + UI)
# =========================================================
.PHONY: rag-dev rag-real-llm rag-full rag-ingest-real backend-dev ui

# RAG dev mode: fake embeddings + fake LLM (no external API usage)
rag-dev:
	@echo ">>> RAG dev mode: fake embeddings + fake LLM (no OpenAI calls)"
	USE_FAKE_EMBEDDINGS=true USE_FAKE_LLM=true $(PYTHON) -m rag_service.ingest
	@echo ">>> Starting backend on http://0.0.0.0:8000 ..."
	USE_FAKE_EMBEDDINGS=true USE_FAKE_LLM=true uvicorn rag_service.main:app --host 0.0.0.0 --port 8000 --reload

# RAG mode: real LLM, fake embeddings (cheap semantic preview)
rag-real-llm:
	@echo ">>> RAG mode: real LLM (gpt-4.1-mini), fake embeddings (no embedding cost)"
	@echo ">>> NOTE: You must have OPENAI_API_KEY and billing configured."
	USE_FAKE_EMBEDDINGS=true USE_FAKE_LLM=false uvicorn rag_service.main:app --host 0.0.0.0 --port 8000 --reload

# RAG full mode: real LLM + real embeddings
rag-full:
	@echo ">>> RAG full mode: real embeddings + real LLM (this may incur OpenAI cost)"
	@echo ">>> Rebuilding embeddings with real model..."
	USE_FAKE_EMBEDDINGS=false USE_FAKE_LLM=false $(PYTHON) -m rag_service.ingest
	@echo ">>> Starting backend on http://0.0.0.0:8000 ..."
	USE_FAKE_EMBEDDINGS=false USE_FAKE_LLM=false uvicorn rag_service.main:app --host 0.0.0.0 --port 8000 --reload

# Just run the backend using whatever is in .env (manual mode)
backend-dev:
	@echo ">>> Starting backend with .env configuration on http://0.0.0.0:8000 ..."
	uvicorn rag_service.main:app --host 0.0.0.0 --port 8000 --reload

# RAG UI (Vite dev server)
ui:
	@echo ">>> Starting rag-ui Vite dev server on http://localhost:5173 ..."
	cd rag-ui && npm run dev

# =========================================================
# Help
# =========================================================
help:
	@echo "Available targets:"
	@echo "  make lint                   - Lint Python (ruff, flake8, black)"
	@echo "  make format                 - Format Python using Black"
	@echo "  make test                   - Run unit & integration tests"
	@echo "  make infra-init             - Terraform init"
	@echo "  make infra-plan             - Terraform plan (show changes)"
	@echo "  make infra-up               - Apply Terraform (build infra)"
	@echo "  make infra-down             - Destroy Terraform-managed infra"
	@echo "  make fetch-data             - Run both fetch-svi and fetch-climate"
	@echo "  make dataproc-create-cluster / dataproc-delete-cluster"
	@echo "  make dbt-run / dbt-test     - Run dbt with local profiles"
