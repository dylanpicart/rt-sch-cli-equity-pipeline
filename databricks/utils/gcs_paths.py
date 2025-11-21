"""
Centralized GCS path definitions for the rt-school-climate pipeline.
"""

BASE_GCS = "gs://rt-school-climate-delta"

bronze_path = f"{BASE_GCS}/bronze/climate"
silver_path = f"{BASE_GCS}/silver/climate_clean"

bronze_checkpoint_path = f"{BASE_GCS}/checkpoints/climate_bronze"
silver_checkpoint_path = f"{BASE_GCS}/checkpoints/climate_silver"
