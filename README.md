# Response Prediction Tool

Upload a CSV of `external_id`s, and this app looks them up in the voterfile, scores them with a PySpark model hosted on a Databricks Model Serving endpoint, and shows the results in the browser.

## Flow

1. User logs in with Google
2. Upload a CSV with an `external_id` column
3. App joins those people against the voterfile + feature table in Databricks and stages them
4. The model scores everyone in the staging table via a Databricks Serving endpoint
5. Predictions are saved to a permanent predictions table
6. The app shows a completion page with KPIs, a prediction breakdown, and a preview of the results (with a full CSV download)