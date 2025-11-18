#!/usr/bin/env python3
"""
fetch_svi_to_gcs.py

Download CDC/ATSDR Social Vulnerability Index (SVI) CSV over HTTP
and upload it to a Google Cloud Storage bucket.

Usage (from repo root):

  python scripts/fetch_svi_to_gcs.py \
    --url "<PASTE_SVI_CSV_URL_HERE>" \
    --bucket rt-school-climate-delta \
    --object raw/svi/cdc_svi.csv

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

DEFAULT_LOCAL_PATH = "data/source_svi/raw/cdc_svi_ny_2022.csv"
DEFAULT_BUCKET = "rt-school-climate-delta"
DEFAULT_OBJECT = "raw/svi/cdc_svi.csv"

# You will paste the actual CDC SVI CSV URL here or pass via --url
DEFAULT_SVI_URL = os.getenv("SVI_CSV_URL", "")

logger = logging.getLogger("fetch_svi_to_gcs")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def http_get_with_retries(
    url: str,
    timeout: int = 30,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
) -> Response:
    """
    Perform a REST-style HTTP GET with basic retry + backoff.

    Retries on network errors, HTTP 5xx, and 429.
    """
    headers = {
        "User-Agent": "rt-school-climate-pipeline/1.0",
        "Accept": "text/csv,application/octet-stream;q=0.9,*/*;q=0.8",
    }

    last_exc: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Requesting SVI CSV (attempt %d): %s", attempt, url)
            resp = requests.get(url, headers=headers, timeout=timeout)
            # Raise for 4xx/5xx
            resp.raise_for_status()

            # Optionally guard against unexpected content types
            content_type = resp.headers.get("Content-Type", "")
            if "csv" not in content_type and "text" not in content_type:
                logger.warning(
                    "Unexpected Content-Type '%s' from %s", content_type, url
                )

            return resp

        except HTTPError as e:
            status = getattr(e.response, "status_code", None)
            logger.error("HTTP error (%s): %s", status, e)

            # Retry only on 5xx or 429
            if status in (429, 500, 502, 503, 504):
                last_exc = e
            else:
                raise

        except (Timeout, RequestException) as e:
            logger.error("Network error: %s", e)
            last_exc = e

        # If we got here, we decided to retry
        if attempt < max_retries:
            sleep = backoff_factor ** (attempt - 1)
            logger.info("Retrying in %.1f seconds...", sleep)
            time.sleep(sleep)

    # Exhausted retries
    logger.error("Failed to fetch SVI CSV after %d attempts", max_retries)
    if last_exc:
        raise last_exc
    raise RuntimeError("Unknown error while fetching SVI CSV")


def download_svi_csv(url: str, dest_path: str) -> str:
    """
    Download SVI CSV from the given URL and save it to dest_path.
    """
    resp = http_get_with_retries(url)
    logger.info("Writing CSV to %s", dest_path)

    # Ensure directory exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return dest_path


def upload_file_to_gcs(local_path: str, bucket_name: str, blob_name: str) -> None:
    """
    Upload a local file to GCS using google-cloud-storage.
    """
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Local file does not exist: {local_path}")

    logger.info(
        "Uploading %s to gs://%s/%s", local_path, bucket_name, blob_name
    )

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)

    logger.info("Upload complete.")


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download CDC SVI CSV and upload to GCS."
    )
    parser.add_argument(
        "--url",
        required=not bool(DEFAULT_SVI_URL),
        default=DEFAULT_SVI_URL or None,
        help=(
            "Direct URL to the CDC SVI CSV (tract-level). "
            "Can also be set via SVI_CSV_URL env var."
        ),
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
        help=f"Local filename for the downloaded CSV (default: {DEFAULT_LOCAL_PATH})",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    setup_logging()
    args = parse_args(argv)

    if not args.url:
        logger.error(
            "No SVI CSV URL provided. Use --url or set SVI_CSV_URL env var."
        )
        return 1

    logger.info("Starting SVI download + upload pipeline...")
    logger.info("Source URL: %s", args.url)
    logger.info("Target GCS: gs://%s/%s", args.bucket, args.object)

    try:
        local_path = download_svi_csv(args.url, args.dest)
        upload_file_to_gcs(local_path, args.bucket, args.object)
        logger.info("SVI CSV successfully ingested into GCS.")
        return 0
    except Exception:
        logger.exception("SVI ingestion failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
