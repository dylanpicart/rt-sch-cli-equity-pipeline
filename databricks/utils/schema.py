from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

# TODO: update with the actual schema of your Kafka climate payload
climate_schema = StructType([
    StructField("school_id", StringType(), True),
    StructField("survey_year", StringType(), True),
    StructField("question_code", StringType(), True),
    StructField("response_value", DoubleType(), True),
])
