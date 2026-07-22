from . import config


def build_staging_query(external_ids):
    """Builds a read-only SELECT against the voterfile + hs_bronze for the given external_ids.

    Joins VOTERFILE_TABLE (external_id) with HS_BRONZE_TABLE (for the hs_*
    model features, keyed on LALVOTERID -- the same identifier as
    external_id, just under a different column name in that table).
    hs_* columns are cast to double to match the model's expected input
    schema, since hs_bronze stores them as strings.
    Returns (sql, params) for use with a parameterized cursor.execute call.
    """
    if not external_ids:
        raise ValueError("external_ids must be a non-empty list")

    select_list = [f"v.`{config.JOIN_KEY}` AS `external_id`"]
    select_list += [f"CAST(h.`{col}` AS DOUBLE) AS `{col}`" for col in config.FEATURE_COLS]

    placeholders = ", ".join(["?"] * len(external_ids))
    sql = (
        f"SELECT {', '.join(select_list)}\n"
        f"FROM {config.VOTERFILE_TABLE} v\n"
        f"JOIN {config.HS_BRONZE_TABLE} h ON v.`{config.JOIN_KEY}` = h.`LALVOTERID`\n"
        f"WHERE v.`{config.JOIN_KEY}` IN ({placeholders})"
    )
    return sql, list(external_ids)


def stage_people(conn, external_ids):
    """Creates/replaces the staging table from the voterfile for external_ids.

    Only ever SELECTs from the voterfile -- writes go to STAGING_TABLE only.
    """
    select_sql, params = build_staging_query(external_ids)
    ctas_sql = f"CREATE OR REPLACE TABLE {config.STAGING_TABLE} AS\n{select_sql}"
    with conn.cursor() as cursor:
        cursor.execute(ctas_sql, params)
