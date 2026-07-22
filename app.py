import os
import tempfile
from functools import wraps

from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, render_template, request, session, url_for

from backend import config
from backend.pipeline import run_pipeline

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY

oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=config.GOOGLE_CLIENT_ID,
    client_secret=config.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_email" not in session:
            return redirect(url_for("login_page"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/login-page", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["GET"])
def login():
    redirect_uri = url_for("login_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri, prompt="select_account")


@app.route("/login/callback", methods=["GET"])
def login_callback():
    token = oauth.google.authorize_access_token()
    user_info = token.get("userinfo") or oauth.google.userinfo()
    email = user_info.get("email", "")

    if not email.endswith(f"@{config.ALLOWED_EMAIL_DOMAIN}"):
        return render_template(
            "login.html",
            error=f"Access is restricted to @{config.ALLOWED_EMAIL_DOMAIN} accounts.",
        )

    session["user_email"] = email
    return redirect(url_for("upload"))


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user_email", None)
    return redirect(url_for("login_page"))


@app.route("/", methods=["GET"])
@login_required
def upload():
    return render_template("upload.html")


@app.route("/run", methods=["POST"])
@login_required
def run():
    csv_file = request.files.get("csv_file")
    if not csv_file or csv_file.filename == "":
        return render_template("upload.html", error="Please choose a CSV file.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, csv_file.filename)
        csv_file.save(csv_path)

        try:
            result = run_pipeline(csv_path)
        except Exception as exc:
            return render_template("upload.html", error=f"Something went wrong: {exc}")

    return render_template("result.html", result=result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("PORT") is None
    app.run(host="0.0.0.0", port=port, debug=debug)
