# tests/integration/test_sanity_integration.py
import pytest


@pytest.mark.integration
def test_integration_marker_sanity():
    """
    Simple integration test placeholder.

    Use `pytest -m integration` to run only integration tests
    once you wire them to real GCS/Snowflake/Dataproc resources.
    """
    assert True
