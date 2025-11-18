from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    IntegerType,
)

# School climate from NYC survey API
school_climate_schema = StructType(
    [
        StructField("dbn", StringType(), True),
        StructField("school_name", StringType(), True),

        # response rates come as strings from source; we will cast in Silver
        StructField("total_parent_response_rate", StringType(), True),
        StructField("total_teacher_response_rate", StringType(), True),
        StructField("total_student_response_rate", StringType(), True),
    ]
)

# Social Vulnerability Index (SVI) schema for svi_raw.csv
svi_schema = StructType(
    [
        # Core geographic identifiers
        StructField("FIPS", StringType(), True),          # census tract FIPS
        StructField("STATE", StringType(), True),         # state name or code
        StructField("ST_ABBR", StringType(), True),       # two-letter state code (optional if present)
        StructField("COUNTY", StringType(), True),        # county name
        StructField("TRACT", StringType(), True),         # tract ID within county

        # Optional helper fields you may add/derive (zip / neighborhood)
        StructField("ZIP_CODE", StringType(), True),
        StructField("NEIGHBORHOOD_NAME", StringType(), True),

        # Overall SVI composite score
        StructField("RPL_THEMES", DoubleType(), True),    # overall SVI percentile / composite

        # Theme-specific indices (names may differ slightly in your CSV → adjust as needed)
        StructField("RPL_THEME1", DoubleType(), True),    # Socioeconomic
        StructField("RPL_THEME2", DoubleType(), True),    # Household comp & disability
        StructField("RPL_THEME3", DoubleType(), True),    # Minority status & language
        StructField("RPL_THEME4", DoubleType(), True),    # Housing & transportation

        # (Optional) population / denominator fields if present
        StructField("E_TOTPOP", IntegerType(), True),     # estimated total population
    ]
)
