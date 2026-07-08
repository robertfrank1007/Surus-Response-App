from databricks import sql

from . import config


def get_connection():
    """Opens a Databricks SQL connection using OAuth user login.

    On first use this opens a browser window for you to log in
    (same login as the Databricks workspace). The resulting token
    is cached locally so later runs won't prompt again until it expires.
    """
    return sql.connect(
        server_hostname=config.DATABRICKS_HOST,
        http_path=config.DATABRICKS_HTTP_PATH,
        auth_type="databricks-oauth",
    )
