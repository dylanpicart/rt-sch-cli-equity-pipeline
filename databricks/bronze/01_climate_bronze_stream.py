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

    raw = (
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
