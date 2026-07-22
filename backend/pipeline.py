import time
from urllib.parse import quote

from . import config, csv_utils, db, inference, predictions, voterfile


def run_pipeline(csv_path, preview_rows=10):
    """Runs the full CSV -> voterfile -> staging -> inference -> predictions flow.

    Returns a dict with a status and a preview of the first `preview_rows`
    scored people, for display in the app's completion view.
    """
    start_time = time.time()

    external_ids = csv_utils.read_external_ids(csv_path)

    conn = db.get_connection()
    try:
        voterfile.stage_people(conn, external_ids)
        scored = inference.score_staging_table(conn)
        predictions.write_predictions(conn, scored)
    finally:
        conn.close()

    num_likely = int((scored["prediction"] == 1.0).sum())
    num_unlikely = len(scored) - num_likely
    num_not_found = len(external_ids) - len(scored)

    preview = scored.head(preview_rows).to_dict(orient="records")
    csv_data_uri = "data:text/csv;charset=utf-8," + quote(scored.to_csv(index=False))
    return {
        "status": "completed",
        "num_requested": len(external_ids),
        "num_scored": len(scored),
        "num_likely": num_likely,
        "num_unlikely": num_unlikely,
        "num_not_found": num_not_found,
        "runtime_seconds": round(time.time() - start_time, 1),
        "staging_table": config.STAGING_TABLE,
        "predictions_table": config.PREDICTIONS_TABLE,
        "preview": preview,
        "csv_data_uri": csv_data_uri,
    }
