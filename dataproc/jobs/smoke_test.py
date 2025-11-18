from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder.appName("SmokeTest").getOrCreate()
    df = spark.range(0, 10)
    print("Count:", df.count())
    df.show()
    spark.stop()

if __name__ == "__main__":
    main()
