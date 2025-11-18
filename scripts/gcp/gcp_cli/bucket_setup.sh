# bucket_setup.sh
#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# bronze
gsutil mkdir gs://rt-school-climate-delta/bronze/
gsutil mkdir gs://rt-school-climate-delta/bronze/school_climate/
gsutil mkdir gs://rt-school-climate-delta/bronze/svi/

# silver
gsutil mkdir gs://rt-school-climate-delta/silver/
gsutil mkdir gs://rt-school-climate-delta/silver/school_climate/
gsutil mkdir gs://rt-school-climate-delta/silver/svi/

# gold
gsutil mkdir gs://rt-school-climate-delta/gold/
gsutil mkdir gs://rt-school-climate-delta/gold/climate_vulnerability/
gsutil mkdir gs://rt-school-climate-delta/gold/participation_rates/
