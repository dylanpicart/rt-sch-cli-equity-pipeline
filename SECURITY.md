# Security Policy

## Overview

This project is a multi-platform data engineering stack spanning **GCP**, **Snowflake**, **Databricks**, **Kafka**, and **GitHub Actions**. It is designed with security and DevSecOps practices in mind:

- No plaintext secrets committed to Git
- Automated secret scanning with `detect-secrets`
- Linting + formatting via pre-commit hooks
- Infrastructure-as-Code with Terraform (pinned provider versions)
- Optional, manual-only CD for dbt and Terraform

---

## Secret Management

### Never commit secrets

The following **must never be committed** to the repository:

- Snowflake passwords
- Databricks PAT tokens
- GCP service account JSON keys
- Kafka API keys & secrets
- `.env` files
- `*.tfvars` files containing real credentials

Secrets are managed via:

- Local **`.env`** (ignored by Git) for development
- **GitHub Actions Secrets** for CI/CD
- **GCP Application Default Credentials** or service accounts for Terraform
- **Databricks Secret Scopes** (optional, for workspace-level secrets)

### detect-secrets

This repo uses [`detect-secrets`](https://github.com/Yelp/detect-secrets) via pre-commit to prevent leaked secrets. A `.secrets.baseline` file is tracked in Git and updated when secrets patterns change.

Before committing:

```bash
pre-commit run --all-files
```

If a secret is detected, **rotate it immediately** in the target platform and update `.env` / GitHub Secrets.

---

## Terraform & IaC

Infrastructure is defined under `infra/terraform/`:

- **GCP**

  - Bronze / Silver / Gold GCS buckets
  - Optional Dataproc cluster (feature-flagged)
  - Service account and IAM bindings for Snowflake

- **Snowflake**

  - Warehouse, database, schemas (`BRONZE`, `SILVER`, `GOLD`, `DBT_*`)
  - Roles (`PIPELINE_ROLE`, `BI_ROLE`)
  - Grants using classic `snowflake_*_grant` resources (Snowflake-Labs provider)
  - GCS-backed storage integration + stage for Bronze

- **Databricks**

  - Optional job cluster and job for Bronze → Silver transformations (feature-flagged)

Provider versions are **pinned** in `providers.tf` to ensure reproducible builds.

Local workflow:

```bash
cd infra/terraform
set -a && source ../../.env && set +a
terraform fmt
terraform init -backend=false
terraform validate
terraform plan -var-file="terraform.dev.tfvars"
```

> `terraform.dev.tfvars` and other env-specific var files are **not committed** (see `.gitignore`). Only `terraform.tfvars.example` should be tracked.

---

## CI / CD Security

### CI (Continuous Integration)

`ci.yml` runs on every push / PR and enforces:

- `pre-commit` (trimming whitespace, EOF, YAML, **detect-secrets**, Black, Ruff, Flake8)
- `pytest` (unit + integration tests)
- `dbt deps` + `dbt compile` (with a dummy profile so no warehouse is hit)
- `terraform fmt -check`, `terraform validate` (using `-chdir=infra/terraform`)

No secrets are required for CI validation (no `terraform apply`, no dbt runs against real Snowflake).

### CD (Continuous Delivery, manual-only)

`cd.yml` is manual (`workflow_dispatch`) and allows:

- Running dbt on **Snowflake** and/or **Databricks** with real credentials from GitHub Secrets
- (Optionally) running `terraform apply` using GitHub Secrets and env-driven `TF_VAR_` variables

Infra changes are **never auto-applied**; they must be explicitly requested via the CD workflow and are separate from CI.

---

## Responsible Disclosure

If you discover a vulnerability:

1. Do not open a public GitHub issue about it.
2. Contact the maintainer directly (via the email in the repo or commit history).
3. Include as much detail as you can to help reproduce the issue.
4. The maintainer will triage and patch the issue as soon as reasonably possible.

---

## Developer Checklist

Before committing:

```bash
pre-commit run --all-files
pytest -q
terraform -chdir=infra/terraform validate
dbt compile --project-dir dbt
```

Before deploying:

```bash
terraform -chdir=infra/terraform plan
# Then (when ready):
terraform -chdir=infra/terraform apply
# Or: trigger the CD workflow in GitHub Actions.
```
