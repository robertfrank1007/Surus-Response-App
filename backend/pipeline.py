from . import csv_utils, db, inference, predictions, voterfile


def run_pipeline(csv_path, preview_rows=10):
    """Runs the full CSV -> voterfile -> staging -> inference -> predictions flow.

    Returns a dict with a status and a preview of the first `preview_rows`
    scored people, for display in the app's completion view.
    """
    external_ids = csv_utils.read_external_ids(csv_path)

    conn = db.get_connection()
    try:
        voterfile.stage_people(conn, external_ids)
        scored = inference.score_staging_table(conn)
        predictions.write_predictions(conn, scored)
    finally:
        conn.close()

    preview = scored.head(preview_rows).to_dict(orient="records")
    return {
        "status": "completed",
        "num_requested": len(external_ids),
        "num_scored": len(scored),
        "preview": preview,
    }
