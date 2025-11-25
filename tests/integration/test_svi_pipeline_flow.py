# tests/integration/test_svi_pipeline_flow.py
import os
import pytest


@pytest.mark.integration
def test_svi_env_config_shape():
    """
    Example integration-style test that checks configuration shape
    for the SVI pipeline without touching external systems.

    Later you can expand this into a real test that:
      - writes sample data to GCS (or a local fake),
      - runs the transformation,
      - asserts Snowflake/GCS outputs.
    """
    gcs_bucket = os.getenv("GCP_BUCKET_NAME") or os.getenv("BUCKET")
    svi_url = os.getenv("SVI_CSV_URL")

    # These don't need to be real in CI, just non-empty when you care about integration runs
    assert svi_url is None or svi_url.startswith("http")
    # Bucket may be None in CI; this check is intentionally loose.
    if gcs_bucket is not None:
        assert isinstance(gcs_bucket, str)
        assert gcs_bucket != ""
