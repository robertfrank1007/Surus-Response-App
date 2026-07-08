import pandas as pd


def read_external_ids(csv_path, column="external_id"):
    df = pd.read_csv(csv_path)
    if column not in df.columns:
        raise ValueError(f"CSV must have a '{column}' column, got: {list(df.columns)}")
    ids = df[column].dropna().astype(str).unique().tolist()
    if not ids:
        raise ValueError("CSV contained no external IDs")
    return ids
