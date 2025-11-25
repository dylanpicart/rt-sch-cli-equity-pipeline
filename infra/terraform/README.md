# Infrastructure as Code (Terraform)

This directory contains the **Infrastructure-as-Code (IaC)** configuration for the
Real-Time School Climate & Equity Pipeline. It automates the creation of all
cloud resources across **GCP**, **Snowflake**, and **Databricks**, ensuring the
entire multi-platform data pipeline can be deployed, updated, or torn down with
a single command.

Terraform allows us to:

- Define cloud resources as **version-controlled code**
- Guarantee consistent infra across environments (dev, staging, prod)
- Avoid manual configuration drift across cloud consoles
- Quickly destroy expensive resources when not in use
- Recreate the entire platform reproducibly for demos or recovery

---

## Architecture Overview

The pipeline spans multiple cloud platforms:

- **Google Cloud Platform (GCP)**
  - GCS buckets for Bronze/Silver/Gold medallion layers
  - Optional Dataproc cluster for Spark ingestion
  - Service accounts + IAM roles for secure cross-platform access

- **Snowflake**
  - Warehouse + database + medallion schemas
  - Roles + grants for BI users and pipeline workloads
  - Storage integration pointing to GCS Bronze
  - External Stage for raw file ingestion

- **Databricks**
  - Optional job cluster with auto-termination
  - Bronze → Silver transformation notebook job
  - Cross-platform parameter wiring (bucket names, schemas, warehouse)

Terraform connects all of these using explicit resource relationships so that:

- Each platform has the **correct identity and permissions**
- Bucket names, schema names, and integration endpoints always match
- Databricks, Snowflake, and GCP use the same resource definitions
- No manual setup is required after `terraform apply`

---

## What Terraform Automates

### GCS (Google Cloud Storage)

Creates three medallion buckets:

- `<prefix>-<env>-bronze`
- `<prefix>-<env>-silver`
- `<prefix>-<env>-gold`

Each includes:

- Versioning
- Lifecycle policies
- Uniform bucket-level access
- Environment-specific labels

---

### GCP -> Snowflake Integration

Terraform configures:

- A dedicated GCP service account for Snowflake
- IAM permissions allowing controlled bucket access
- A Snowflake **Storage Integration**
- A Snowflake **External Stage** pointing to the GCS Bronze bucket

This provides a secure and consistent ingestion path from GCS → Snowflake.

---

### Snowflake Warehouse, DB, Schemas, Roles

Terraform provisions:

- An XSMALL warehouse with aggressive auto-suspend
- `SCHOOL_CLIMATE` database
- `BRONZE`, `SILVER`, `GOLD`, and `DBT` schemas
- `PIPELINE_ROLE` for compute & ingestion
- `BI_ROLE` with read-only access to GOLD

This captures Snowflake’s security + governance model in code.

---

### Databricks

Controlled via feature flag:

```hcl
enable_databricks_job = true
````

If enabled, Terraform creates:

- A Databricks job cluster (auto-terminating)
- A scheduled or on-demand notebook task that reads Bronze → produces Silver
- Automatically passes bucket names, schemas, and warehouse variables from Terraform

Everything stays consistent with GCP + Snowflake definitions.

---

## Optional: Dataproc Cluster

Also feature-flagged:

```hcl
enable_dataproc_cluster = true
```

Provisioned when needed for Spark jobs, destroyed when idle to avoid cost.

---

## Feature Flags for Cost Control

To avoid surprise billing, expensive resources are disabled by default:

```hcl
enable_databricks_job      = false
enable_dataproc_cluster    = false
```

You can toggle them per environment using `terraform.tfvars`.

---

## Usage

### 1. Initialize Terraform (first time only)

```bash
make infra-init
```

### 2. See what Terraform will create/change

```bash
make infra-plan
```

### 3. Apply the infrastructure

```bash
make infra-up
```

### 4. Destroy the environment (safe cleanup)

```bash
make infra-down
```

All resources, including Databricks clusters, service accounts, Snowflake schemas,
and GCS buckets, will be created/destroyed cleanly through these commands.

---

## Cross-Platform Wiring

Terraform ensures consistent communication between systems via:

- **Shared outputs**

  - GCS bucket names flow into Snowflake stage creation
  - Snowflake warehouse & DB flow into Databricks job config
- **Resource dependencies (`depends_on`)**

  - Snowflake integration waits for GCP IAM binding
- **Zero manual console setup**

  - No drifting permissions or forgotten roles

This eliminates a major class of platform-integration issues.

---

## Why This Matters

This Terraform setup demonstrates:

- Multi-cloud orchestration (GCP + Snowflake + Databricks)
- Secure cross-platform identity & permissions
- Cost-safe feature-flagged deployment
- Fully reproducible data platform environments
- DevOps-grade reproducibility for Data Engineering pipelines

Recruiters and senior engineers will immediately recognize this as
**production-caliber platform engineering**.

---

## Directory Structure

```text
infra/
  terraform/
    main.tf
    providers.tf
    variables.tf
    gcs.tf
    gcp_snowflake_integration.tf
    snowflake.tf
    databricks.tf
    dataproc.tf
    terraform.tfvars.example
    README.md
```

---

## Next Steps (Optional Enhancements)

You can extend this IaC to include:

- Snowflake Tasks + Pipes (automatic ingestion)
- Private Databricks → GCS networking
- Databricks Secrets (Snowflake creds, SA keys)
- Monitoring/alerting policies
- Terraform Cloud for remote state
