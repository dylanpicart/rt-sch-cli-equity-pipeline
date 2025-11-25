"""
Snowflake connection options for the Spark connector.

These values are loaded securely from the Databricks secret scope
'rt-school-climate', which is backed by GCP Secret Manager.

Do NOT hard-code credentials here. All secrets should live in GCP.
"""

from typing import Dict, Optional

from databricks.sdk.runtime import dbutils

_SCOPE = "rt-school-climate"


def get_sf_options(
    *,
    database: Optional[str] = None,
    schema: Optional[str] = None,
    warehouse: Optional[str] = None,
    role: Optional[str] = None,
) -> Dict[str, str]:
    """
    Build a Snowflake options dict for spark.read/write.format("snowflake").

    Parameters
    ----------
    database : str, optional
        Override the default Snowflake database from secrets.
    schema : str, optional
        Override the default Snowflake schema from secrets.
    warehouse : str, optional
        Override the default Snowflake warehouse from secrets.
    role : str, optional
        Override the default Snowflake role from secrets.

    Returns
    -------
    Dict[str, str]
        Options suitable for use with the Spark Snowflake connector.
    """
    # Account is stored as the Snowflake account identifier, e.g. "iswglex-bw25896".
    # We append ".snowflakecomputing.com" to form the full URL.
    sf_account = dbutils.secrets.get(_SCOPE, "sf_account")

    return {
        "sfURL": f"{sf_account}.snowflakecomputing.com",
        "sfUser": dbutils.secrets.get(_SCOPE, "sf_user"),
        "sfPassword": dbutils.secrets.get(_SCOPE, "sf_password"),
        "sfRole": role or dbutils.secrets.get(_SCOPE, "sf_role"),
        "sfWarehouse": warehouse or dbutils.secrets.get(_SCOPE, "sf_warehouse"),
        "sfDatabase": database or dbutils.secrets.get(_SCOPE, "sf_database"),
        "sfSchema": schema or dbutils.secrets.get(_SCOPE, "sf_schema"),
    }
