#!/bin/sh
set -e

echo "========================================="
echo "Running DIGIT database migrations"
echo "DB_URL: $DB_URL"
echo "========================================="

run_migration() {
    SERVICE=$1
    SCHEMA_TABLE=$2
    LOCATIONS=$3

    echo ""
    echo "--- Migrating: $SERVICE ---"
    echo "Schema table: $SCHEMA_TABLE"
    echo "Locations: $LOCATIONS"

    flyway \
      -url="$DB_URL" \
      -table="$SCHEMA_TABLE" \
      -user="$FLYWAY_USER" \
      -password="$FLYWAY_PASSWORD" \
      -locations="$LOCATIONS" \
      -baselineOnMigrate=true \
      -outOfOrder=true \
      -ignoreMigrationPatterns="*:missing" \
      migrate

    echo "--- $SERVICE migrations completed ---"
}

# Run migrations for each service
# Each service has its own schema_version table to track migrations independently
#
# Skipped (schema already in db/full-dump.sql — re-running Flyway would duplicate DDL):
#   egov-hrms, egov-user, egov-workflow-v2
# Skipped mdms-v2: dump has eg_mdms_data / eg_mdms_schema_definition and mdms_schema_version;
# Flyway here uses mdms_v2_schema_version so migrate would re-apply CREATEs and fail.

# Skipped public-service / public-service-init: dump already has public.service
# (access-control module registry); it has no service_code column, so studio DDL + FKs fail.

if [ -d "/flyway/sql/health-individual" ]; then
    run_migration "health-individual" "health_individual_schema_version" "filesystem:/flyway/sql/health-individual"
fi

if [ -d "/flyway/sql/health-service-request" ]; then
    run_migration "health-service-request" "egov_health_service_request_schema_version" "filesystem:/flyway/sql/health-service-request"
fi

echo ""
echo "========================================="
echo "All migrations completed successfully!"
echo "========================================="
