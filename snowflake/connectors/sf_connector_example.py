# Example: write gold climate-vulnerability table from Delta to Snowflake

from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Example: reading gold Delta table already materialized in Databricks
GOLD_TABLE_NAME = "gold_climate_vulnerability"
df_gold = spark.table(GOLD_TABLE_NAME)

sfOptions = {
    "sfURL": "<ACCOUNT>.snowflakecomputing.com",
    "sfUser": "<SNOWFLAKE_USER>",
    "sfPassword": "<SNOWFLAKE_PASSWORD>",
    "sfDatabase": "EDU_ANALYTICS",
    "sfSchema": "CLIMATE_EQUITY",
    "sfWarehouse": "COMPUTE_WH",
    "sfRole": "DATA_ENGINEER_ROLE",
}

df_gold.write.format("snowflake") \
    .options(**sfOptions) \
    .option("dbtable", "SCHOOL_CLIMATE_GOLD") \
    .mode("overwrite") \
    .save()
