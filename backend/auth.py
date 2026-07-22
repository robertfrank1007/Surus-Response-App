import requests

from . import config

_CLIENT_ID = "databricks-cli"


def get_access_token():
    """Exchanges the long-lived refresh token for a fresh short-lived access token.

    Plain HTTP call to Databricks' OAuth endpoint -- no CLI, no browser, no
    local cache file. Works the same on a laptop or a headless server.
    """
    response = requests.post(
        f"https://{config.DATABRICKS_HOST}/oidc/v1/token",
        data={
            "grant_type": "refresh_token",
            "client_id": _CLIENT_ID,
            "refresh_token": config.DATABRICKS_REFRESH_TOKEN,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]
