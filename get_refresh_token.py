"""One-time script to get a Databricks OAuth refresh token for this app.

Run this once (`python get_refresh_token.py`), log in via the browser
window it opens, and copy the printed refresh token into .env as
DATABRICKS_REFRESH_TOKEN. Uses Databricks' own pre-registered "databricks-cli"
public OAuth client, requesting the broad "all-apis" scope so the resulting
token works for both SQL queries and Model Serving endpoint calls.
"""
import base64
import hashlib
import http.server
import secrets
import threading
import urllib.parse
import webbrowser

import requests

from backend import config

REDIRECT_PORT = 8020
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"
CLIENT_ID = "databricks-cli"
SCOPE = "all-apis offline_access"

_result = {}


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        _result["code"] = params.get("code", [None])[0]
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Login complete. You can close this tab.</h1>")

    def log_message(self, *args):
        pass


def main():
    host = f"https://{config.DATABRICKS_HOST}"

    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")

    auth_url = f"{host}/oidc/v1/authorize?" + urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": secrets.token_urlsafe(16),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    })

    http.server.HTTPServer.allow_reuse_address = True
    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), _CallbackHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()

    print("Opening browser to log in...")
    webbrowser.open(auth_url)
    thread.join(timeout=120)

    code = _result.get("code")
    if not code:
        print("Login failed or timed out -- try again.")
        return

    response = requests.post(
        f"{host}/oidc/v1/token",
        data={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier,
        },
    )
    response.raise_for_status()
    refresh_token = response.json()["refresh_token"]

    print("\nSuccess! Add this line to your .env file:\n")
    print(f"DATABRICKS_REFRESH_TOKEN={refresh_token}\n")


if __name__ == "__main__":
    main()
