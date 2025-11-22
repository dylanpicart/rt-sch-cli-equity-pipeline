-- In documentation (safe)
CREATE OR REPLACE STAGE gcs_stage
  URL = 'gs://${GCP_BUCKET_NAME}/raw/'
  STORAGE_INTEGRATION = GCS_INT;
