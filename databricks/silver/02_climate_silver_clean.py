from pyspark.sql.functions import col, trim

from utils.gcs_paths import bronze_path, silver_path


def main():
    """
    Silver batch job:
    - Reads Bronze Delta table
    - Cleans and casts key fields
    - Writes a curated Silver Delta table
    """
    bronze_df = spark.read.format("delta").load(bronze_path)

    silver_df = (
        bronze_df
        .withColumn("survey_year", col("survey_year").cast("int"))
        .withColumn("school_id", trim(col("school_id")))
        # TODO: add more cleaning and standardization here
    )

    (
        silver_df.write
        .format("delta")
        .mode("overwrite")
        .save(silver_path)
    )


if __name__ == "__main__":
    main()
