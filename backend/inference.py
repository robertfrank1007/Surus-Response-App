import pandas as pd
import requests

from . import auth, config


def _read_staging_table(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {config.STAGING_TABLE}")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


def score_staging_table(conn):
    """Scores every row in the staging table via the Model Serving endpoint.

    Returns a DataFrame with external_id + prediction columns.
    `prediction` is the 0.0/1.0 class label. The endpoint's default output
    only includes the hard label, not a probability score.
    """
    df = _read_staging_table(conn)
    if df.empty:
        raise ValueError(f"{config.STAGING_TABLE} has no rows to score")

    token = auth.get_access_token()
    feature_df = df[config.FEATURE_COLS]
    records = [
        {col: (None if pd.isna(value) else value) for col, value in row.items()}
        for row in feature_df.to_dict(orient="records")
    ]

    response = requests.post(
        config.ENDPOINT_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"dataframe_records": records},
        timeout=120,
    )
    response.raise_for_status()
    predictions = [int(p) for p in response.json()["predictions"]]

    return pd.DataFrame({
        "external_id": df["external_id"],
        "prediction": predictions,
    })
