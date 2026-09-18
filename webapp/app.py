"""
Two tiny "sites" for practicing Google Password Manager.

Each site is a completely independent little Flask app with its own users
and its own port, so they look like two unrelated websites to your browser.
That's the point: Chrome scopes saved passwords to the site's origin
(scheme + host + port), so a password saved for "Nimbus Bank" on :5000
will never be offered to autofill on "Pixel Outfitters" at :5001.

Nothing here is a real security boundary -- it's an in-memory dict that
resets every time the process restarts. The interesting thing to watch
is entirely on the browser side: the "Save password?" prompt, the little
key icon offering a generated password, and autofill kicking in (or not).
"""

import hashlib
from datetime import datetime

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

SITES = {
    "bank": {
        "name": "Nimbus Bank",
        "tagline": "Not a real bank. Please don't wire us anything.",
        "accent": "#1a5276",
        "port": 5000,
    },
    "shop": {
        "name": "Pixel Outfitters",
        "tagline": "Definitely not a real store either.",
        "accent": "#6c3483",
        "port": 5001,
    },
}

# A handful of SHA-1 hashes for extremely common passwords, matching the
# demo corpus in password_checkup_from_scratch.py. Used only for the "this
# looks like a breached password" banner -- a toy stand-in for the real
# Password Checkup feature, which uses k-anonymity to check a much bigger
# list without ever learning your actual password.
BREACHED_HASHES = {
    hashlib.sha1(pw.encode()).hexdigest()
    for pw in [
        "password", "password123", "123456", "123456789", "qwerty",
        "letmein", "admin", "welcome", "monkey", "dragon",
    ]
}


def looks_breached(password: str) -> bool:
    return hashlib.sha1(password.encode()).hexdigest() in BREACHED_HASHES


def create_app(site_key: str) -> Flask:
    if site_key not in SITES:
        raise ValueError(f"unknown site {site_key!r}, expected one of {list(SITES)}")

    site = SITES[site_key]
    app = Flask(__name__)
    app.secret_key = f"classroom-demo-only-{site_key}"  # fine for a local demo, never for real
    app.config["SITE"] = site
    app.config["SITE_KEY"] = site_key

    # In-memory "database": email -> {password_hash, created_at}
    users: dict[str, dict] = {}

    @app.context_processor
    def inject_site():
        return {"site": site, "logged_in_email": session.get("email")}

    @app.route("/")
    def home():
        return render_template("home.html", user_count=len(users))

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        error = None
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("new-password", "")
            confirm = request.form.get("confirm-password", "")

            if not email or not password:
                error = "Email and password are required."
            elif password != confirm:
                error = "Passwords don't match."
            elif email in users:
                error = "An account with that email already exists -- try logging in."
            else:
                users[email] = {
                    "password_hash": generate_password_hash(password),
                    "created_at": datetime.utcnow().isoformat(),
                    "breached_warning_shown": looks_breached(password),
                }
                session["email"] = email
                return redirect(url_for("dashboard"))

        return render_template("signup.html", error=error)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("current-password", "")
            record = users.get(email)

            if record and check_password_hash(record["password_hash"], password):
                session["email"] = email
                return redirect(url_for("dashboard"))
            error = "Incorrect email or password."

        return render_template("login.html", error=error)

    @app.route("/dashboard")
    def dashboard():
        email = session.get("email")
        if not email or email not in users:
            return redirect(url_for("login"))
        record = users[email]
        return render_template(
            "dashboard.html",
            email=email,
            created_at=record["created_at"],
            breached_warning=record["breached_warning_shown"],
        )

    @app.route("/change-password", methods=["GET", "POST"])
    def change_password():
        email = session.get("email")
        if not email or email not in users:
            return redirect(url_for("login"))

        error = None
        success = False
        if request.method == "POST":
            current = request.form.get("current-password", "")
            new = request.form.get("new-password", "")
            confirm = request.form.get("confirm-password", "")
            record = users[email]

            if not check_password_hash(record["password_hash"], current):
                error = "Current password is incorrect."
            elif new != confirm:
                error = "New passwords don't match."
            elif not new:
                error = "New password can't be empty."
            else:
                record["password_hash"] = generate_password_hash(new)
                record["breached_warning_shown"] = looks_breached(new)
                success = True

        return render_template("change_password.html", error=error, success=success, email=email)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("home"))

    return app


if __name__ == "__main__":
    import sys

    site_key = sys.argv[1] if len(sys.argv) > 1 else "bank"
    app = create_app(site_key)
    # 0.0.0.0 so this is reachable from outside a Docker container, not just
    # from within it. Fine for a local classroom demo; not for the open internet.
    app.run(host="0.0.0.0", port=SITES[site_key]["port"], debug=True, use_reloader=False)
