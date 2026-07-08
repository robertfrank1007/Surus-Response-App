from . import config


def ensure_predictions_table(conn):
    ddl = (
        f"CREATE TABLE IF NOT EXISTS {config.PREDICTIONS_TABLE} ("
        "external_id STRING, "
        "prediction STRING, "
        "score DOUBLE, "
        "scored_at TIMESTAMP"
        ")"
    )
    with conn.cursor() as cursor:
        cursor.execute(ddl)


def write_predictions(conn, predictions_df, batch_size=500):
    """Appends external_id + prediction + score rows to PREDICTIONS_TABLE."""
    ensure_predictions_table(conn)

    rows = list(
        predictions_df[["external_id", "prediction", "score"]].itertuples(
            index=False, name=None
        )
    )
    with conn.cursor() as cursor:
        for start in range(0, len(rows), batch_size):
            batch = rows[start:start + batch_size]
            values_sql = ", ".join(["(?, ?, ?, current_timestamp())"] * len(batch))
            params = [
                value
                for row in batch
                for value in (row[0], str(row[1]), float(row[2]))
            ]
            cursor.execute(
                f"INSERT INTO {config.PREDICTIONS_TABLE} (external_id, prediction, score, scored_at) "
                f"VALUES {values_sql}",
                params,
            )
