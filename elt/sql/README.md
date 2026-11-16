# FreshCart SQL scripts

Execution order:
1. `01_setup_tables_steps_06_10.sql` — create Bronze, Silver and Gold objects.
2. `02_load_and_transform_steps_11_15.sql` — append the eight reconstructed raw records, normalize, validate, quarantine and deduplicate. Run this baseline load only once.
3. `03_corrected_rebuild_steps_12_15.sql` — optional correction/rebuild from existing Bronze data; it does not reload Bronze. Use this instead of repeating the Step 11 INSERT.
4. `04_scd2_gold_quality_steps_16_20.sql` — SCD Type 2, Gold publication, rerun checks and quality-check demonstration.

**Data note:** The supplied scripts explicitly describe the sample records as reconstructed because the original classroom FreshCart data/notebook was not provided. Loyalty-point multipliers are assumptions in the script and should be checked against the official specification. Run in your own authorised Snowflake environment and verify outputs before claiming execution.
