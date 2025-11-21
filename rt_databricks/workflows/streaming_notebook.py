from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, expr
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

spark = SparkSession.builder.appName("SchoolClimateStreaming").getOrCreate()

kafka_bootstrap = "<your-kafka-bootstrap>"
kafka_topic = "school_climate_stream"

raw_stream = (
    spark.readStream
         .format("kafka")
         .option("kafka.bootstrap.servers", kafka_bootstrap)
         .option("subscribe", kafka_topic)
         .option("startingOffsets", "latest")
         .load()
)

# Example schema for your climate JSON
climate_schema = StructType([
    StructField("dbn", StringType(), True),
    StructField("school_name", StringType(), True),
    StructField("year", IntegerType(), True),
    StructField("climate_score", DoubleType(), True),
    StructField("borough", StringType(), True),
    StructField("tract_fips", StringType(), True),  # ensure this is provided or derived
])

parsed = (
    raw_stream
        .selectExpr("CAST(value AS STRING) as json_str")
        .select(from_json(col("json_str"), climate_schema).alias("data"))
        .select("data.*")
)

# Write to a Delta "bronze" table in DBFS
query = (
    parsed.writeStream
          .format("delta")
          .outputMode("append")
          .option("checkpointLocation", "/checkpoints/bronze_climate")
          .start("/delta/bronze_climate")
)

query.awaitTermination()
