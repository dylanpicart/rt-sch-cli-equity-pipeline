"""
Helpers for constructing canonical GCS paths for the school-climate pipeline.

These functions standardize how all Bronze, Silver, and streaming checkpoint
paths are built inside your GCS bucket `rt-school-climate-delta`.

Final structure:

  gs://rt-school-climate-delta/rt_school_climate/bronze/<dataset>/
  gs://rt-school-climate-delta/rt_school_climate/silver/<dataset>/
  gs://rt-school-climate-delta/rt_school_climate/_checkpoints/<stream_name>/

This keeps your Databricks > GCS > Snowflake pipeline consistent and clean.
"""

from __future__ import annotations
from typing import Optional


# Your actual bucket on GCS
BUCKET: str = "rt-school-climate-delta"
BASE_PREFIX: str = "rt_school_climate"


def _join_path(*parts: str) -> str:
    """Join path fragments with single slashes, ignoring empty or None parts."""
    cleaned = [str(p).strip().strip("/") for p in parts if p and str(p).strip()]
    return "/".join(cleaned)


def _gcs_uri(*parts: str) -> str:
    """Return a full GCS URI (gs://bucket/path...)."""
    path = _join_path(*parts)
    return f"gs://{BUCKET}/{path}"


def bronze_path(
    dataset: str,
    *subdirs: str,
    filename: Optional[str] = None,
) -> str:
    """
    Return the canonical GCS path for Bronze datasets.

    Example:
    >>> bronze_path("school_climate_raw")
    'gs://rt-school-climate-delta/rt_school_climate/bronze/school_climate_raw'
    """
    parts = [BASE_PREFIX, "bronze", dataset, *subdirs]
    if filename:
        parts.append(filename)
    return _gcs_uri(*parts)


def silver_path(
    dataset: str,
    *subdirs: str,
    filename: Optional[str] = None,
) -> str:
    """
    Return the canonical GCS path for Silver datasets.

    Example:
    >>> silver_path("student_metrics_clean", "year=2025")
    'gs://rt-school-climate-delta/rt_school_climate/silver/student_metrics_clean/year=2025'
    """
    parts = [BASE_PREFIX, "silver", dataset, *subdirs]
    if filename:
        parts.append(filename)
    return _gcs_uri(*parts)


def checkpoint_path(stream_name: str) -> str:
    """
    Return the GCS path for Structured Streaming checkpoints.

    Example:
    >>> checkpoint_path("kafka_school_climate_bronze")
    'gs://rt-school-climate-delta/rt_school_climate/_checkpoints/kafka_school_climate_bronze'
    """
    return _gcs_uri(BASE_PREFIX, "_checkpoints", stream_name)
