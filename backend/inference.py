import mlflow
import mlflow.lightgbm
import pandas as pd

from . import config


def load_model():
    """Loads the model via the LightGBM-native flavor.

    mlflow.pyfunc.load_model's generic schema enforcement insists string
    columns stay as plain object dtype, but the LightGBM model underneath
    needs those same columns as pandas "category" dtype (how they were
    trained) to match categorical features correctly. Loading the native
    flavor skips that overly strict generic check.
    """
    mlflow.set_tracking_uri("databricks")
    mlflow.set_registry_uri("databricks-uc")
    return mlflow.lightgbm.load_model(config.MODEL_URI)


def _get_input_schema():
    mlflow.set_tracking_uri("databricks")
    mlflow.set_registry_uri("databricks-uc")
    return mlflow.models.get_model_info(config.MODEL_URI).signature.inputs


def _read_staging_table(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {config.STAGING_TABLE}")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


_MLFLOW_TO_PANDAS_DTYPE = {
    "boolean": "boolean",
    "integer": "Int32",
    "long": "Int64",
    "float": "float32",
    "double": "float64",
    "string": "category",
}


def _coerce_to_model_schema(df, schema):
    """Casts df's columns to match the model's saved input signature exactly.

    Databricks numeric columns come back as wider Python/pandas types (e.g.
    int64) than what the model was logged with (e.g. int32), and string
    columns need to be pandas "category" dtype to match LightGBM's trained
    categorical features.
    """
    df = df.copy()
    for spec in schema.inputs:
        dtype = _MLFLOW_TO_PANDAS_DTYPE.get(spec.type.name)
        if dtype is None or spec.name not in df.columns:
            continue
        if dtype in ("Int32", "Int64", "float32", "float64"):
            df[spec.name] = pd.to_numeric(df[spec.name], errors="coerce").astype(dtype)
        else:
            df[spec.name] = df[spec.name].astype(dtype)
    return df


def score_staging_table(conn, model=None):
    """Runs the model over every row currently in the staging table.

    Returns a DataFrame with external_id + prediction + score columns.
    `prediction` is the 0/1 class label; `score` is the probability of
    class 1, for ranking/prioritizing people within a label.
    """
    df = _read_staging_table(conn)
    if df.empty:
        raise ValueError(f"{config.STAGING_TABLE} has no rows to score")

    model = model or load_model()
    schema = _get_input_schema()
    X = _coerce_to_model_schema(df[config.FEATURE_COLS], schema)
    predictions = model.predict(X)
    scores = model.predict_proba(X)[:, 1].round(2)

    return pd.DataFrame({
        "external_id": df["external_id"],
        "prediction": predictions,
        "score": scores,
    })
