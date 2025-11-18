# Databricks: one-time/batch load of SVI CSV -> Delta Silver

from pyspark.sql import functions as F
from databricks.utils.schema import svi_schema

SVI_CSV_PATH = "/FileStore/tables/svi_raw.csv"  # upload via Databricks UI
SVI_SILVER_PATH = "/mnt/delta/silver_svi"

df_svi = (
    spark.read.csv(SVI_CSV_PATH, header=True, schema=svi_schema)
    .withColumn("load_ts", F.current_timestamp())
)

df_svi.write.format("delta").mode("overwrite").save(SVI_SILVER_PATH)

# Optionally, create Delta table for easier access from SQL:
spark.sql(
    f"""
    CREATE OR REPLACE TABLE silver_svi
    USING DELTA
    LOCATION '{SVI_SILVER_PATH}'
    """
)
