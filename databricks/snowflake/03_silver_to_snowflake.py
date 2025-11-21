from utils.snowflake_options import sf_options
from utils.gcs_paths import silver_path


def main():
    """
    Silver -> Snowflake loader:
    - Reads Silver Delta table from GCS
    - Writes it into Snowflake as CLIMATE_CLEAN
    """
    df = spark.read.format("delta").load(silver_path)

    (
        df.write
        .format("snowflake")
        .options(**sf_options)
        .option("dbtable", "CLIMATE_CLEAN")
        .mode("overwrite")
        .save()
    )


if __name__ == "__main__":
    main()
