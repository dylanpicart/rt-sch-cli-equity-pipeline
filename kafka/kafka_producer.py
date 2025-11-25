#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kafka Producer for NYC School Climate Data
------------------------------------------
Pulls climate survey data from NYC Open Data and streams it into
the Kafka topic `school_climate_stream` on Confluent Cloud.

This script includes:
- Config loading from producer_config.json
- Optional lightweight data-contract validation
- Safe retry + logging
"""

import os
import json
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

import requests
from confluent_kafka import Producer

load_dotenv()

# -------------------------------------------------------------------
# Paths & Constants
# -------------------------------------------------------------------

CONFIG_PATH = Path(__file__).parent / "config" / "producer_config.json"
TOPIC_NAME = "school_climate_stream"

# NYC Open Data – School Climate Survey API (sample feed)
NYC_SCHOOL_CLIMATE_API = os.getenv(
    "NYC_SCHOOL_CLIMATE_API",
    "https://data.cityofnewyork.us/api/views/fb6n-h22r/rows.json?accessType=DOWNLOAD",
)

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s"
)

# -------------------------------------------------------------------
# Minimal Data Contract (optional but recommended)
# -------------------------------------------------------------------

REQUIRED_FIELDS = [
    "dbn",
    "school_name",
    "total_parent_response_rate",
    "total_teacher_response_rate",
    "total_student_response_rate",
]


def is_valid_event(row: dict) -> bool:
    """For now, log missing fields but don't block production."""
    missing = [
        f for f in REQUIRED_FIELDS if f not in row or row[f] in (None, "", "NULL")
    ]
    if missing:
        logging.debug("Row missing expected fields %s; still producing.", missing)
    return True


# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Kafka config not found: {path}")
    with path.open() as f:
        return json.load(f)


def create_producer(config: dict) -> Producer:
    """Initialize Confluent Kafka producer."""
    return Producer(config)


def fetch_school_climate_data() -> list[dict]:
    """Fetch latest climate survey records and normalize to list[dict]."""
    try:
        resp = requests.get(NYC_SCHOOL_CLIMATE_API, timeout=30)
        resp.raise_for_status()
        payload = resp.json()

        # Case 1: already a list of dicts (for /resource/<id>.json style)
        if isinstance(payload, list):
            return payload

        # Case 2: Socrata /api/views/.../rows.json style: { meta: {...}, data: [...] }
        if isinstance(payload, dict) and "data" in payload and "meta" in payload:
            columns_meta = payload["meta"]["view"]["columns"]
            col_names = [c.get("fieldName") for c in columns_meta]

            records: list[dict] = []
            for row_vals in payload["data"]:
                row_dict = {name: value for name, value in zip(col_names, row_vals)}
                records.append(row_dict)

            return records

        logging.error("Unexpected payload format from NYC API: %s", type(payload))
        return []

    except Exception as e:
        logging.error("Failed to fetch NYC data: %s", e)
        return []


# -------------------------------------------------------------------
# Main Loop
# -------------------------------------------------------------------


def main(poll_interval_sec: int = 15) -> None:

    conf = load_config(CONFIG_PATH)
    producer = create_producer(conf)

    logging.info("🚀 Kafka Producer started")
    logging.info("Topic: %s", TOPIC_NAME)
    logging.info("Config loaded from: %s", CONFIG_PATH)

    while True:
        rows = fetch_school_climate_data()
        if not rows:
            logging.warning("No records fetched. Retrying after sleep...")
            time.sleep(poll_interval_sec)
            continue

        logging.info("Fetched %d records from NYC API", len(rows))

        valid_count = 0
        skipped_count = 0

        for row in rows:

            # Validate against lightweight data contract
            if not is_valid_event(row):
                skipped_count += 1
                continue

            producer.produce(TOPIC_NAME, value=json.dumps(row).encode("utf-8"))
            valid_count += 1

        producer.flush()
        logging.info(
            "Produced %d messages, skipped %d invalid. Sleeping %s sec...",
            valid_count,
            skipped_count,
            poll_interval_sec,
        )

        time.sleep(poll_interval_sec)


# -------------------------------------------------------------------

if __name__ == "__main__":
    main()
