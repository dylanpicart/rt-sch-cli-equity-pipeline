#!/usr/bin/env python3
"""
fetch_climate_to_gcs.py

Download NYC School Climate data from NYC Open Data API (JSON)
and upload it to a Google Cloud Storage bucket.

Usage (from repo root):

  python scripts/fetch_climate_to_gcs.py \
    --bucket rt-school-climate-delta \
    --object raw/climate/nyc_school_climate_raw.json

You must have GOOGLE_APPLICATION_CREDENTIALS set to a service account
JSON with write access to the target bucket.
"""

import argparse
import logging
import os
import sys
import time
from typing import Optional

import requests
from google.cloud import storage
from requests import Response
from requests.exceptions import HTTPError, Timeout, RequestException

DEFAULT_LOCAL_PATH = "data/source_climate/raw/nyc_school_climate_raw.json"
DEFAULT_BUCKET = "rt-school-climate-delta"
DEFAULT_OBJECT = "raw/climate/nyc_school_climate_raw.json"

# NYC Open Data School Climate API (your link)
DEFAULT_CLIMATE_URL = os.getenv(
    "CLIMATE_API_URL",
    "https://data.cityofnewyork.us/api/views/fb6n-h22r/rows.json?accessType=DOWNLOAD",
)

logger = logging.getLogger("fetch_climate_to_gcs")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def http_get_with_retries(
    url: str,
    timeout: int = 60,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
) -> Response:
    """
    REST-style HTTP GET with basic retry/backoff.

    Retries on network errors, HTTP 5xx, and 429.
    """
    headers = {
        "User-Agent": "rt-school-climate-pipeline/1.0",
        "Accept": "application/json",
    }

    last_exc: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Requesting NYC climate JSON (attempt %d): %s", attempt, url)
            resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
            resp.raise_for_status()
            return resp

        except HTTPError as e:
            status = getattr(e.response, "status_code", None)
            logger.error("HTTP error (%s): %s", status, e)
            if status in (429, 500, 502, 503, 504):
                last_exc = e
            else:
                raise

        except (Timeout, RequestException) as e:
            logger.error("Network error: %s", e)
            last_exc = e

        if attempt < max_retries:
            sleep = backoff_factor ** (attempt - 1)
            logger.info("Retrying in %.1f seconds...", sleep)
            time.sleep(sleep)

    logger.error("Failed to fetch climate JSON after %d attempts", max_retries)
    if last_exc:
        raise last_exc
    raise RuntimeError("Unknown error while fetching climate JSON")


def download_climate_json(url: str, dest_path: str) -> str:
    resp = http_get_with_retries(url)
    logger.info("Writing JSON to %s", dest_path)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return dest_path



def upload_file_to_gcs(local_path: str, bucket_name: str, blob_name: str) -> None:
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Local file does not exist: {local_path}")

    logger.info("Uploading %s to gs://%s/%s", local_path, bucket_name, blob_name)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)

    logger.info("Upload complete.")


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download NYC School Climate JSON and upload to GCS."
    )
    parser.add_argument(
        "--url",
        required=False,
        default=DEFAULT_CLIMATE_URL,
        help="NYC Open Data climate API URL. Can also be set via CLIMATE_API_URL.",
    )
    parser.add_argument(
        "--bucket",
        default=DEFAULT_BUCKET,
        help=f"GCS bucket name (default: {DEFAULT_BUCKET})",
    )
    parser.add_argument(
        "--object",
        default=DEFAULT_OBJECT,
        help=f"GCS object path/key (default: {DEFAULT_OBJECT})",
    )
    parser.add_argument(
        "--dest",
        default=DEFAULT_LOCAL_PATH,
        help=f"Local filename for downloaded JSON (default: {DEFAULT_LOCAL_PATH})",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    setup_logging()
    args = parse_args(argv)

    if not args.url:
        logger.error(
            "No climate API URL provided. Use --url or set CLIMATE_API_URL env var."
        )
        return 1

    logger.info("Starting climate download + upload pipeline...")
    logger.info("Source URL: %s", args.url)
    logger.info("Target GCS: gs://%s/%s", args.bucket, args.object)

    try:
        local_path = download_climate_json(args.url, args.dest)
        upload_file_to_gcs(local_path, args.bucket, args.object)
        logger.info("Climate JSON successfully ingested into GCS.")
        return 0
    except Exception:
        logger.exception("Climate ingestion failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
