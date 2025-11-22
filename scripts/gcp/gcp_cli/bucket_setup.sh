# bucket_setup.sh
#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# bronze
gsutil mkdir gs://gcp-project-bucket/bronze/
gsutil mkdir gs://gcp-project-bucket/bronze/school_climate/
gsutil mkdir gs://gcp-project-bucket/bronze/svi/

# silver
gsutil mkdir gs://gcp-project-bucket/silver/
gsutil mkdir gs://gcp-project-bucket/silver/school_climate/
gsutil mkdir gs://gcp-project-bucket/silver/svi/

# gold
gsutil mkdir gs://gcp-project-bucket/gold/
gsutil mkdir gs://gcp-project-bucket/gold/climate_vulnerability/
gsutil mkdir gs://gcp-project-bucket/gold/participation_rates/