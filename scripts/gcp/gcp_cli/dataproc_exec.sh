#!/bin/bash



# Set PROJECT_ID variable
PROJECT_ID=$(gather=$(gcloud config get-value project); echo $gather)
# Submit the Dataproc batch job with Kafka integration
gcloud dataproc batches submit pyspark \
  gs://rt-school-climate-delta/kafka/kafka_streaming.py \
  --project="${PROJECT_ID}" \
  --region=us-east1 \
  --batch=school-climate-stream \
  --version=1.1 \
  --properties="spark.jars.packages=org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.4" \
  -- \
    --bucket=rt-school-climate-delta \
    --bootstrap-servers="pkc-619z3.us-east1.gcp.confluent.cloud:9092" \
    --kafka-username="2T67Z24IQPQFDEDM" \
    --kafka-password="cfltWWrIe63JrWAKBC4qNoY0HDPjRm4MGB0z7heIrM/q6om/BOfXRyjM32alBgVg"

# Clean up checkpoint directories (if needed)
gsutil -m rm -r gs://rt-school-climate-delta/bronze_school_climate_chk || true
gsutil -m rm -r gs://rt-school-climate-delta/silver_school_climate_chk || true
