gcloud config set project rt-school-climate

PROJECT_ID="rt-school-climate"

# Create sf_user
echo -n "ANON_USER" | gcloud secrets create sf_user \
  --project="$PROJECT_ID" \
  --replication-policy="automatic" \
  --data-file=-

# Create sf_password
echo -n 'p@ssw0R9' | gcloud secrets create sf_password \
  --project="$PROJECT_ID" \
  --replication-policy="automatic" \
  --data-file=-

# Create sf_account
echo -n "randoms-co0321" | gcloud secrets create sf_account \
  --project="$PROJECT_ID" \
  --replication-policy="automatic" \
  --data-file=-

# Create sf_role
echo -n "SOME_SF_ROLE" | gcloud secrets create sf_role \
  --project="$PROJECT_ID" \
  --replication-policy="automatic" \
  --data-file=-

# Create sf_warehouse
echo -n "PSOME_WAREHOUSE" | gcloud secrets create sf_warehouse \
  --project="$PROJECT_ID" \
  --replication-policy="automatic" \
  --data-file=-

# Create sf_database
echo -n "SNOWFLAKE_DATABASE_NAME" | gcloud secrets create sf_database \
  --project="$PROJECT_ID" \
  --replication-policy="automatic" \
  --data-file=-

# Create sf_schema
echo -n "SOME_SF_SCHEMA" | gcloud secrets create sf_schema \
  --project="$PROJECT_ID" \
  --replication-policy="automatic" \
  --data-file=-

# Grant access to service account
PROJECT_ID="rt-school-climate"
SA_EMAIL="databricks-email@rt-school-climate.iam.gserviceaccount.com"

for SECRET in sf_user sf_password sf_account sf_role sf_warehouse sf_database sf_schema; do
  gcloud secrets add-iam-policy-binding "$SECRET" \
    --project="$PROJECT_ID" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor"
done
