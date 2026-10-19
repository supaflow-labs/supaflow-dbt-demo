# Local Snowflake validation

Validated on 2026-10-16 UTC (2026-10-15 Pacific) with dbt Core 1.12.0,
dbt-snowflake 1.12.0, Snowflake CLI connection `dev`, and database `SUPA_DB`.

The complete `bash scripts/validate.sh` sequence exited zero against the final
`SUPAFLOW_DEMO` namespace:

| Command | Result |
| --- | --- |
| `dbt debug` | Connection and configuration checks pass |
| `dbt deps` | Pass; no external packages, so dbt prints its no-packages warning |
| `dbt parse` | Pass |
| `dbt list --resource-type model` | 16 models |
| `dbt compile` | Pass |
| `dbt seed --full-refresh` | 10 seeds, 230 synthetic rows |
| `dbt run --full-refresh` | 13 views and 3 tables |
| `dbt snapshot` | 15 current subscriber versions |
| `dbt test` | 68 data tests pass |
| `dbt build --full-refresh` | 10 seeds, 16 models, 1 snapshot, 68 tests and 1 hook pass; zero errors, warnings or skips in the build summary |
| `dbt source freshness` | All 10 sources pass |
| `dbt docs generate` | Catalog and docs artifacts generated |
| `dbt show --select expansion_audience --limit 10` | 2 eligible customers |
| `dbt show --select demo_results --limit 10` | Readable audience result with invoice amounts and product |
| `dbt show --select excluded_customers --limit 20` | 13 customers with reasons |

Independent Snowflake checks confirm all 213 physical seed columns match the
recorded type contracts. The generated typed comparison SQL compared every field
in all 230 seed rows with the CSV payloads: zero missing or unexpected rows across
all 10 relations. Uniqueness tests additionally reject duplicate keys.

The final tables contain 15 customer profiles, 2 eligible customers, and 13 excluded
customers. Northstar has 12,200 paid and zero overdue; Orchard has 11,800 paid, 2,000
unpaid but not yet due, and zero overdue. Snapshot reruns leave 15 total versions,
all current, confirming idempotence when subscriber data has not changed.

An earlier full command sequence also passed in a separate, initially empty
verification namespace. Final validation corrected a redundant snapshot schema
prefix and removed a legacy analysis whose name conflicted with the audience
model's selection. The final snapshot is in `SUPAFLOW_DEMO_SNAPSHOTS`.

The Git-import and command-runner workflow inside the Supaflow application is a
subsequent validation step. NetSuite structures remain a documented synthetic
subset pending live-account metadata verification. No ingestion or activation is
claimed by these dbt checks. Machine-specific logs, connection profiles and raw
runtime artifacts are excluded from Git.
