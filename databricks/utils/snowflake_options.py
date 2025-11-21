"""
Snowflake connection options for the Spark connector.

These values are loaded securely from the Databricks secret scope
'rt-school-climate', which is backed by GCP Secret Manager.

Do NOT hard-code credentials here. All secrets should live in GCP.
"""

from pyspark.dbutils import DBUtils  # available in Databricks runtime

# 'spark' is injected by Databricks in jobs/notebooks
dbutils = DBUtils(spark)

_scope = "rt-school-climate"

sf_options = {
    "sfURL": f"{dbutils.secrets.get(_scope, 'sf_account')}.snowflakecomputing.com",
    "sfUser": dbutils.secrets.get(_scope, "sf_user"),
    "sfPassword": dbutils.secrets.get(_scope, "sf_password"),
    "sfRole": dbutils.secrets.get(_scope, "sf_role"),
    "sfWarehouse": dbutils.secrets.get(_scope, "sf_warehouse"),
    "sfDatabase": dbutils.secrets.get(_scope, "sf_database"),
    "sfSchema": dbutils.secrets.get(_scope, "sf_schema"),
}
