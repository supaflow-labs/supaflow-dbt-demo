#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Use DBT_PROFILES_DIR or pass --profiles-dir /private/path as arguments.
dbt debug "$@"
dbt deps "$@"
dbt parse "$@"
dbt list --resource-type model "$@"
dbt compile "$@"
dbt seed --full-refresh "$@"
dbt run --full-refresh "$@"
dbt snapshot "$@"
dbt test "$@"
dbt build --full-refresh "$@"
dbt source freshness "$@"
dbt docs generate "$@"
dbt show --select expansion_audience --limit 10 "$@"
dbt show --select demo_results --limit 10 "$@"
dbt show --select excluded_customers --limit 20 "$@"
