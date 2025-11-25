#!/usr/bin/env python3
"""
dataproc/jobs/load_svi_to_snowflake.py

Batch job to:
  - Read CDC SVI NY 2022 CSV from GCS
  - Standardize tract FIPS
  - Load into Snowflake as BRONZE.SVI_NY_RAW
"""

import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lpad

load_dotenv()

DEFAULT_GCS_SVI_PATH = os.getenv(
    "GCS_SVI_PATH", "gs://gcs-bucket-name/raw/svi/cdc_svi_ny_2022.csv"
)


def get_snowflake_options(spark: SparkSession) -> tuple[dict, str, str]:
    """
    Read Snowflake connection options from Spark configuration.
    We expect these to be provided via spark.* properties passed
    in the Dataproc --properties-file.
    """
    conf = spark.conf

    # Path to SVI CSV in GCS (overrideable via spark.svi.gcsPath)
    gcs_svi_path = conf.get("spark.svi.gcsPath", DEFAULT_GCS_SVI_PATH)

    sf_account = conf.get("spark.snowflake.account", None)
    sf_user = conf.get("spark.snowflake.user", None)
    sf_password = conf.get("spark.snowflake.password", None)
    sf_role = conf.get("spark.snowflake.role", None)
    sf_warehouse = conf.get("spark.snowflake.warehouse", None)
    sf_database = conf.get("spark.snowflake.database", "SCHOOL_CLIMATE")
    sf_schema = conf.get("spark.snowflake.schema", "BRONZE")
    sf_table = conf.get("spark.snowflake.table", "SVI_NY_RAW")

    missing = [
        name
        for name, value in [
            ("spark.snowflake.account", sf_account),
            ("spark.snowflake.user", sf_user),
            ("spark.snowflake.password", sf_password),
            ("spark.snowflake.role", sf_role),
            ("spark.snowflake.warehouse", sf_warehouse),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(
            f"Missing required Snowflake Spark properties: {', '.join(missing)}"
        )

    sf_options = {
        "sfURL": f"{sf_account}.snowflakecomputing.com",
        "sfUser": sf_user,
        "sfPassword": sf_password,
        "sfRole": sf_role,
        "sfWarehouse": sf_warehouse,
        "sfDatabase": sf_database,
        "sfSchema": sf_schema,
    }

    return sf_options, gcs_svi_path, sf_table


def main():
    spark = SparkSession.builder.appName("LoadSVINYToSnowflake").getOrCreate()

    sf_options, gcs_svi_path, target_table = get_snowflake_options(spark)

    print(f"Reading SVI CSV from: {gcs_svi_path}")
    svi_raw = (
        spark.read.option("header", "true")
        .option("inferSchema", "true")
        .csv(gcs_svi_path)
    )

    print("Raw columns:", svi_raw.columns)

    if "FIPS" not in svi_raw.columns:
        raise RuntimeError("Expected column 'FIPS' not found in SVI CSV schema.")

    svi_clean = svi_raw.withColumnRenamed("FIPS", "tract_fips").withColumn(
        "tract_fips", lpad(col("tract_fips").cast("string"), 11, "0")
    )

    select_cols = ["tract_fips"]
    for c in ["RPL_THEME1", "RPL_THEME2", "RPL_THEME3", "RPL_THEME4", "RPL_THEMES"]:
        if c in svi_clean.columns:
            select_cols.append(c)

    svi_final = svi_clean.select(*select_cols)

    print("Sample rows before Snowflake write:")
    for row in svi_final.limit(5).collect():
        print(row)

    print(
        f"Writing to Snowflake: {sf_options['sfDatabase']}.{sf_options['sfSchema']}.{target_table}"
    )
    (
        svi_final.write.format("snowflake")
        .options(**sf_options)
        .option("dbtable", target_table)
        .mode("overwrite")
        .save()
    )

    print("Snowflake write complete.")
    spark.stop()


if __name__ == "__main__":
    main()
