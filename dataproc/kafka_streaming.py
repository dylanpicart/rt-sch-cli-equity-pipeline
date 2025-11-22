import os
import argparse

from pyspark.sql import SparkSession, functions as F, types as T


def get_args():
    parser = argparse.ArgumentParser(
        description="Stream NYC School Climate data from Kafka to GCS (Bronze/Silver)."
    )
    parser.add_argument(
        "--bootstrap-servers",
        default=os.getenv("KAFKA_BOOTSTRAP"),
        help="Kafka bootstrap servers (Confluent Cloud).",
    )
    parser.add_argument(
        "--kafka-topic",
        default=os.getenv("KAFKA_TOPIC", "school_climate_stream"),
        help="Kafka topic name.",
    )
    parser.add_argument(
        "--kafka-username",
        default=os.getenv("KAFKA_USERNAME"),
        help="Kafka SASL username (Confluent API key).",
    )
    parser.add_argument(
        "--kafka-password",
        default=os.getenv("KAFKA_PASSWORD"),
        help="Kafka SASL password (Confluent API secret).",
    )
    parser.add_argument(
        "--bucket",
        required=True,
        help="GCS bucket name (without gs://), e.g. bucket-name",
    )
    return parser.parse_args()


def build_school_climate_schema() -> T.StructType:
    """Schema for the JSON produced by your Kafka producer."""
    return T.StructType(
        [
            T.StructField("dbn", T.StringType(), True),
            T.StructField("school_name", T.StringType(), True),
            T.StructField("total_parent_response_rate", T.StringType(), True),
            T.StructField("total_teacher_response_rate", T.StringType(), True),
            T.StructField("total_student_response_rate", T.StringType(), True),
        ]
    )


def main():
    args = get_args()

    if not (args.bootstrap_servers and args.kafka_username and args.kafka_password):
        raise ValueError(
            "Missing Kafka connection details. "
            "Set KAFKA_BOOTSTRAP, KAFKA_USERNAME, KAFKA_PASSWORD or pass flags."
        )

    bronze_path = f"gs://{args.bucket}/bronze/school_climate"
    silver_path = f"gs://{args.bucket}/silver/school_climate"

    spark = (
        SparkSession.builder.appName("school-climate-kafka-stream")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    # ---- 1. Read from Kafka (Confluent Cloud) ----
    kafka_options = {
        "kafka.bootstrap.servers": args.bootstrap_servers,
        "subscribe": args.kafka_topic,
        "startingOffsets": "latest",
        "kafka.security.protocol": "SASL_SSL",
        "kafka.sasl.mechanism": "PLAIN",
        # JAAS config is the standard way to provide username/password to Spark Kafka connector
        "kafka.sasl.jaas.config": (
            "org.apache.kafka.common.security.plain.PlainLoginModule required "
            f"username='{args.kafka_username}' password='{args.kafka_password}';"
        ),
    }

    df_kafka = (
        spark.readStream.format("kafka")
        .options(**kafka_options)
        .load()
    )

    # value is binary -> cast to string, keep Kafka timestamp as metadata
    df_raw = df_kafka.select(
        F.col("value").cast("string").alias("value"),
        F.col("timestamp").alias("kafka_timestamp"),
    )

    # ---- 2. Bronze: write raw JSON to GCS ----
    bronze_query = (
        df_raw.writeStream.outputMode("append")
        .format("parquet")
        .option("path", bronze_path)
        .option("checkpointLocation", bronze_path + "/_checkpoint")
        .start()
    )

    # ---- 3. Silver: parse JSON into typed columns and clean ----
    school_climate_schema = build_school_climate_schema()

    df_parsed = (
        df_raw.withColumn(
            "json", F.from_json("value", school_climate_schema)
        )
        .select(
            "json.*",
            "kafka_timestamp",
        )
    )

    df_silver = (
        df_parsed
        .withColumn(
            "parent_response_rate",
            F.col("total_parent_response_rate").cast("double"),
        )
        .withColumn(
            "teacher_response_rate",
            F.col("total_teacher_response_rate").cast("double"),
        )
        .withColumn(
            "student_response_rate",
            F.col("total_student_response_rate").cast("double"),
        )
        .drop(
            "total_parent_response_rate",
            "total_teacher_response_rate",
            "total_student_response_rate",
        )
    )

    silver_query = (
        df_silver.writeStream.outputMode("append")
        .format("parquet")
        .option("path", silver_path)
        .option("checkpointLocation", silver_path + "/_checkpoint")
        .start()
    )

    # Keep both streams running
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
