from databricks import sql

from . import auth, config


def get_connection():
    """Opens a Databricks SQL connection using a bearer token from auth.py.

    Token comes from exchanging DATABRICKS_REFRESH_TOKEN -- no browser,
    no CLI, no local cache file needed, so this works the same on a
    deployed server as it does locally.
    """
    return sql.connect(
        server_hostname=config.DATABRICKS_HOST,
        http_path=config.DATABRICKS_HTTP_PATH,
        access_token=auth.get_access_token(),
    )
