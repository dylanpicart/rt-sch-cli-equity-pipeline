"""
Silver transform for the school-climate pipeline.

Reads raw Bronze Delta (Kafka -> Delta), parses the `value` JSON column,
applies cleaning and normalization, and writes a flattened Silver Delta
table to GCS. Optionally loads curated Silver into Snowflake.

Schema tuned to actual sample payload from Bronze.
"""

from __future__ import annotations

from typing import Optional

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window

from rt_databricks.utils.gcs_paths import bronze_path, silver_path
from rt_databricks.utils.snowflake_options import get_sf_options


# ---------------------------------------------------------------------------
#  Schema helpers
# ---------------------------------------------------------------------------

def get_bronze_value_schema() -> T.StructType:
    """
    JSON schema based on actual sample payload from Bronze.
    """
    return T.StructType([
        T.StructField(":sid", T.StringType(), True),
        T.StructField(":id", T.StringType(), True),
        T.StructField(":position", T.IntegerType(), True),
        T.StructField(":created_at", T.LongType(), True),
        T.StructField(":created_meta", T.StringType(), True),
        T.StructField(":updated_at", T.LongType(), True),
        T.StructField(":updated_meta", T.StringType(), True),
        T.StructField(":meta", T.StringType(), True),

        # Meaningful fields
        T.StructField("dbn", T.StringType(), True),
        T.StructField("school_name", T.StringType(), True),

        T.StructField("total_parent_response_rate", T.StringType(), True),
        T.StructField("total_teacher_response_rate", T.StringType(), True),
        T.StructField("total_student_response_rate", T.StringType(), True),
    ])


# ---------------------------------------------------------------------------
#  Bronze → Silver transforms
# ---------------------------------------------------------------------------

def read_bronze(
    spark: SparkSession,
    bronze_dataset: str = "school_climate_raw",
) -> DataFrame:
    path = bronze_path(bronze_dataset)
    return spark.read.format("delta").load(path)


def transform_bronze_to_silver(bronze_df: DataFrame) -> DataFrame:
    """
    Transform Bronze -> Silver based on actual schema.
    """
    schema = get_bronze_value_schema()

    parsed_df = bronze_df.withColumn(
        "payload",
        F.from_json(F.col("value").cast("string"), schema)
    )

    df = parsed_df.select(
        # Identity fields
        F.col("payload.dbn").alias("dbn"),
        F.col("payload.school_name").alias("school_name"),

        # Response rates
        F.col("payload.total_parent_response_rate").cast("double").alias("parent_response_rate"),
        F.col("payload.total_teacher_response_rate").cast("double").alias("teacher_response_rate"),
        F.col("payload.total_student_response_rate").cast("double").alias("student_response_rate"),

        # Metadata timestamps
        F.to_timestamp(F.from_unixtime("payload.:created_at")).alias("created_at"),
        F.to_timestamp(F.from_unixtime("payload.:updated_at")).alias("updated_at"),

        # Kafka metadata
        F.col("topic").alias("kafka_topic"),
        F.col("partition").alias("kafka_partition"),
        F.col("offset").alias("kafka_offset"),
        F.col("timestamp").alias("event_ts"),
        F.col("ingest_ts"),
    )

        # Add district_number and borough derived from DBN
    df = df.withColumn(
        "district_number",
        F.col("dbn").substr(1, 2).cast("int"),
    )

    df = df.withColumn(
        "borough",
        F.when(F.col("dbn").substr(3, 1) == F.lit("M"), F.lit("Manhattan"))
         .when(F.col("dbn").substr(3, 1) == F.lit("X"), F.lit("Bronx"))
         .when(F.col("dbn").substr(3, 1) == F.lit("K"), F.lit("Brooklyn"))
         .when(F.col("dbn").substr(3, 1) == F.lit("Q"), F.lit("Queens"))
         .when(F.col("dbn").substr(3, 1) == F.lit("R"), F.lit("Staten Island"))
         .otherwise(F.lit(None).cast("string"))
    )

    # Add load timestamp
    df = df.withColumn("load_ts", F.current_timestamp())

    # (Optional) Add dedupe logic when we know which fields define uniqueness
    # For now, return df as-is:
    return df


def write_silver_delta(
    silver_df: DataFrame,
    silver_dataset: str = "school_climate_clean",
    mode: str = "overwrite",
) -> str:

    path = silver_path(silver_dataset)
    (
        silver_df.write
        .format("delta")
        .mode(mode)
        .option("overwriteSchema", "true")
        .save(path)
    )
    return path


# ---------------------------------------------------------------------------
#  Snowflake loader
# ---------------------------------------------------------------------------

def write_silver_to_snowflake(
    silver_df: DataFrame,
    table_name: str = "SCHOOL_CLIMATE_CLEAN",
    *,
    database: Optional[str] = None,
    schema: str = "SILVER",
    mode: str = "overwrite",
) -> None:

    sf_options = get_sf_options(database=database, schema=schema)

    (
        silver_df.write
        .format("snowflake")
        .options(**sf_options)
        .option("dbtable", table_name)
        .mode(mode)
        .save()
    )


# ---------------------------------------------------------------------------
#  Orchestrator
# ---------------------------------------------------------------------------

def run_silver_pipeline(
    spark: SparkSession,
    *,
    bronze_dataset: str = "school_climate_raw",
    silver_dataset: str = "school_climate_clean",
    snowflake_table: Optional[str] = "SCHOOL_CLIMATE_CLEAN",
    write_mode: str = "overwrite",
) -> None:

    bronze_df = read_bronze(spark, bronze_dataset=bronze_dataset)
    silver_df = transform_bronze_to_silver(bronze_df)

    silver_path_written = write_silver_delta(
        silver_df, silver_dataset=silver_dataset, mode=write_mode
    )
    print(f"Wrote Silver Delta to: {silver_path_written}")

    if snowflake_table:
        write_silver_to_snowflake(
            silver_df,
            table_name=snowflake_table,
            mode=write_mode,
        )
        print(f"Loaded Silver into Snowflake table: {snowflake_table}")
