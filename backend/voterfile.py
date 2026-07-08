from . import config


def _feature_select_expr(col):
    if col == "age_days":
        return f"datediff(current_date(), `{config.BIRTHDATE_COL}`) AS `age_days`"
    if col == "reg_tenure_days":
        return f"datediff(current_date(), `{config.REGISTERED_AT_COL}`) AS `reg_tenure_days`"
    return f"`{col}` AS `{col}`"


def build_staging_query(external_ids):
    """Builds a read-only SELECT against the voterfile for the given external_ids.

    Returns (sql, params) for use with a parameterized cursor.execute call.
    """
    if not external_ids:
        raise ValueError("external_ids must be a non-empty list")

    select_list = [f"`{config.JOIN_KEY}` AS `external_id`"]
    select_list += [_feature_select_expr(col) for col in config.FEATURE_COLS]

    placeholders = ", ".join(["?"] * len(external_ids))
    sql = (
        f"SELECT {', '.join(select_list)}\n"
        f"FROM {config.VOTERFILE_TABLE}\n"
        f"WHERE `{config.JOIN_KEY}` IN ({placeholders})"
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
