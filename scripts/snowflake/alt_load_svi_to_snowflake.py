#!/usr/bin/env python3
"""
alt_load_svi_to_snowflake.py

Alternative (non-Spark) loader for SVI NY 2022 → Snowflake BRONZE.SVI_NY_RAW.

Use this when:
  - You want to reload SVI without Dataproc/Spark, or
  - Dataproc has network/e-gres issues reaching Snowflake.

Pipeline:
  GCS (CSV) -> pandas -> Snowflake (BRONZE.SVI_NY_RAW)
"""

import os
import io

import pandas as pd
from google.cloud import storage
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

# GCS source
GCS_BUCKET = "rt-school-climate-delta"
GCS_BLOB = "raw/svi/cdc_svi_ny_2022.csv"

# Snowflake config from environment (.env)
SF_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SF_USER = os.getenv("SNOWFLAKE_USER")
SF_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SF_ROLE = os.getenv("SNOWFLAKE_ROLE")
SF_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SF_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "SCHOOL_CLIMATE")
SF_SCHEMA_BRONZE = os.getenv("SNOWFLAKE_SCHEMA_BRONZE", "BRONZE")
SF_TABLE = os.getenv("SF_SVI_TABLE", "SVI_NY_RAW")


def download_svi_csv_to_dataframe() -> pd.DataFrame:
    """Download the SVI CSV from GCS and return as a pandas DataFrame."""
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(GCS_BLOB)

    if not blob.exists():
        raise FileNotFoundError(
            f"GCS object gs://{GCS_BUCKET}/{GCS_BLOB} does not exist."
        )

    print(f"Downloading gs://{GCS_BUCKET}/{GCS_BLOB} ...")
    data = blob.download_as_bytes()

    # Read with FIPS as string to preserve leading zeros
    df = pd.read_csv(io.BytesIO(data), dtype={"FIPS": "string"})
    print(f"Downloaded SVI CSV with shape: {df.shape}")
    return df


def transform_svi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize FIPS -> tract_fips (11-char) and select key SVI vulnerability columns.

    This mirrors the Spark transformation:
      - FIPS -> tract_fips (string, zfilled to 11)
      - Keep RPL_THEME1–4, RPL_THEMES if present
    """
    if "FIPS" not in df.columns:
        raise KeyError("Expected column 'FIPS' in SVI CSV")

    df = df.copy()
    df["tract_fips"] = df["FIPS"].astype("string").str.zfill(11)

    cols = ["tract_fips"]
    for c in ["RPL_THEME1", "RPL_THEME2", "RPL_THEME3", "RPL_THEME4", "RPL_THEMES"]:
        if c in df.columns:
            cols.append(c)

    df_out = df[cols]
    print("Transformed SVI DataFrame columns:", df_out.columns.tolist())
    print("Sample rows:")
    print(df_out.head())
    return df_out


def connect_snowflake():
    """Create a Snowflake connection using environment variables."""
    missing = [
        name
        for name, value in [
            ("SNOWFLAKE_ACCOUNT", SF_ACCOUNT),
            ("SNOWFLAKE_USER", SF_USER),
            ("SNOWFLAKE_PASSWORD", SF_PASSWORD),
            ("SNOWFLAKE_ROLE", SF_ROLE),
            ("SNOWFLAKE_WAREHOUSE", SF_WAREHOUSE),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing Snowflake env vars: {', '.join(missing)}")

    print(f"Connecting to Snowflake account {SF_ACCOUNT} as {SF_USER}...")
    conn = snowflake.connector.connect(
        user=SF_USER,
        password=SF_PASSWORD,
        account=SF_ACCOUNT,
        warehouse=SF_WAREHOUSE,
        database=SF_DATABASE,
        schema=SF_SCHEMA_BRONZE,
        role=SF_ROLE,
    )
    return conn


def load_svi_to_snowflake():
    """End-to-end run: GCS → pandas → Snowflake BRONZE.SVI_NY_RAW."""
    df_raw = download_svi_csv_to_dataframe()
    df_svi = transform_svi(df_raw)

    conn = connect_snowflake()
    try:
        print(
            f"Writing DataFrame to Snowflake {SF_DATABASE}.{SF_SCHEMA_BRONZE}.{SF_TABLE} ..."
        )
        success, nchunks, nrows, _ = write_pandas(
            conn,
            df_svi,
            table_name=SF_TABLE,
            schema=SF_SCHEMA_BRONZE,
            database=SF_DATABASE,
            quote_identifiers=True,
            auto_create_table=True,
            overwrite=True,
        )
        print(f"write_pandas success={success}, chunks={nchunks}, rows={nrows}")
    finally:
        conn.close()
        print("Closed Snowflake connection.")


if __name__ == "__main__":
    load_svi_to_snowflake()
