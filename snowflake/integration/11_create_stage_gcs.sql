CREATE OR REPLACE STAGE gcs_stage
  URL='gs://rt-school-climate-delta/raw/'
  STORAGE_INTEGRATION = GCS_INT;
