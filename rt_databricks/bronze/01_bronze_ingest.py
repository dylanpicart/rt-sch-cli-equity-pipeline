from pyspark.sql.functions import *
from pyspark.sql.types import *

from utils.config import get_kafka_options
from utils.schema import climate_schema
from utils.gcs_paths import bronze_path, bronze_checkpoint_path


def main():
    """
    Bronze streaming job:
    - Reads JSON records from Kafka (Confluent Cloud)
    - Parses them into typed columns using climate_schema
    - Appends to Delta Bronze table in GCS with checkpoints
    """
    kafka_options = get_kafka_options()

    raw = ("""
Bronze ingestion utilities: Kafka -> Delta on GCS.

This module is responsible for landing *raw* Kafka events into the Bronze layer
in GCS using Delta Lake, with minimal transformation and rich metadata.

Design:
- Keep records as close to raw as possible (schema-on-read at Silver).
- Store Kafka metadata (topic, partition, offset, timestamp).
- Add `ingest_ts` to track when the pipeline wrote the record.
- Use Delta + Structured Streaming with proper checkpointing.

Typical usage from a Databricks notebook:

    from rt_databricks.bronze.bronze_ingest import (
        build_confluent_kafka_options,
        start_kafka_bronze_stream,
    )

    kafka_options = build_confluent_kafka_options(
        bootstrap_servers="<your_bootstrap>",
        sasl_username="<your_api_key>",
        sasl_password="<your_api_secret>",
        starting_offsets="earliest"
    )

    query = start_kafka_bronze_stream(
        spark=spark,
        topic="school_climate_stream",
        stream_name="kafka_school_climate_bronze",
        bronze_dataset="school_climate_raw",
        kafka_options=kafka_options,
    )
"""

from __future__ import annotations
from typing import Dict

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import current_timestamp

from rt_databricks.utils.gcs_paths import bronze_path, checkpoint_path


# ---------------------------------------------------------------------------
# Kafka options helpers
# ---------------------------------------------------------------------------

def build_confluent_kafka_options(
    *,
    bootstrap_servers: str,
    sasl_username: str,
    sasl_password: str,
    security_protocol: str = "SASL_SSL",
    sasl_mechanism: str = "PLAIN",
    starting_offsets: str = "latest",
    group_id: str | None = None,
) -> Dict[str, str]:
    """
    Build Kafka options for Confluent Cloud for use with spark.readStream.
    Uses shaded LoginModule required for Databricks runtimes.
    """

    # IMPORTANT: shaded LoginModule required on Databricks runtimes
    jaas = (
        'kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required '
        f'username="{sasl_username}" '
        f'password="{sasl_password}";'
    )

    options: Dict[str, str] = {
        "kafka.bootstrap.servers": bootstrap_servers,
        "kafka.security.protocol": security_protocol,
        "kafka.sasl.mechanism": sasl_mechanism,
        "kafka.sasl.jaas.config": jaas,
        "startingOffsets": starting_offsets,
        "failOnDataLoss": "false",
    }

    # Optional – not required for Structured Streaming
    if group_id:
        options["kafka.group.id"] = group_id

    return options


# ---------------------------------------------------------------------------
# Core Bronze ingestion logic
# ---------------------------------------------------------------------------

def read_kafka_stream(
    spark: SparkSession,
    topic: str,
    kafka_options: Dict[str, str],
) -> DataFrame:
    """
    Create a streaming DataFrame from Kafka for the given topic.
    """
    reader = (
        spark.readStream
        .format("kafka")
        .option("subscribe", topic)
    )

    for k, v in kafka_options.items():
        reader = reader.option(k, v)

    return reader.load()


def build_bronze_df(kafka_df: DataFrame) -> DataFrame:
    """
    Convert raw Kafka binary columns into Bronze-friendly schema:
    - key/value as STRING
    - preserve Kafka metadata
    - add ingest_ts
    """
    return (
        kafka_df
        .selectExpr(
            "CAST(key AS STRING) AS key",
            "CAST(value AS STRING) AS value",
            "topic",
            "partition",
            "offset",
            "timestamp",
            "timestampType"
        )
        .withColumn("ingest_ts", current_timestamp())
    )


def start_kafka_bronze_stream(
    *,
    spark: SparkSession,
    topic: str,
    stream_name: str,
    bronze_dataset: str,
    kafka_options: Dict[str, str],
):
    """
    Start a Structured Streaming job that ingests Kafka into Bronze Delta on GCS.
    """
    kafka_df = read_kafka_stream(spark=spark, topic=topic, kafka_options=kafka_options)
    bronze_df = build_bronze_df(kafka_df)

    output_path = bronze_path(bronze_dataset)
    chk_path = checkpoint_path(stream_name)

    query = (
        bronze_df.writeStream
        .format("delta")
        .option("checkpointLocation", chk_path)
        .option("path", output_path)
        .outputMode("append")
        .start()
    )

    return query

        spark.readStream
            .format("kafka")
            .options(**kafka_options)
            .load()
    )

    parsed = (
        raw
        .selectExpr("CAST(value AS STRING) AS value_str")
        .select(from_json(col("value_str"), climate_schema).alias("data"))
        .select("data.*")
    )

    query = (
        parsed.writeStream
            .format("delta")
            .option("checkpointLocation", bronze_checkpoint_path)
            .option("path", bronze_path)
            .outputMode("append")
            .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
