-- Run with the Snowflake CLI dev connection after dbt builds EXPANSION_AUDIENCE.
-- Keep date-only values as ISO text at the extraction boundary. This avoids
-- JDBC timezone conversion changing the calendar day before SFMC receives it.
CREATE OR REPLACE TABLE SUPA_DB.SUPAFLOW_DEMO.SFMC_EXPANSION_AUDIENCE AS
SELECT * REPLACE (TO_CHAR(AS_OF_DATE, 'YYYY-MM-DD') AS AS_OF_DATE)
FROM SUPA_DB.SUPAFLOW_DEMO.EXPANSION_AUDIENCE;
