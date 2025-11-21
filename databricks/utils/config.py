import os


def get_kafka_options():
    """
    Returns Kafka options for Confluent Cloud.

    TODO:
    - Replace the default placeholders with real environment variables
      or Databricks secrets.
    """
    return {
        "kafka.bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "<your-bootstrap>"),
        "subscribe": os.getenv("KAFKA_TOPIC", "<your-topic>"),
        "kafka.security.protocol": "SASL_SSL",
        "kafka.sasl.mechanism": "PLAIN",
        "kafka.sasl.username": os.getenv("KAFKA_API_KEY", "<your-api-key>"),
        "kafka.sasl.password": os.getenv("KAFKA_API_SECRET", "<your-api-secret>"),
        "startingOffsets": "latest",
    }
