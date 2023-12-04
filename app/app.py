from flask import Flask, render_template, redirect, request, session, url_for
import hashlib
import os

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config")

@app.route("/")
def index():
    print(app.config["SECRET_KEY"])
    return render_template("index.html", title="PyMart Intranet System | Welcome", page="landing")

@app.route("/login", methods=["GET", "POST"])
def login():
    errors = []
    if request.method == "POST":
        # Get login form data.
        username = request.form.get("username")
        password = request.form.get("password")
        print("Username:", username)
        print("Password:", password)

        # TODO: Validate data.


        # TODO: Check database and compare login information.
        valid_credentials = True
        print("Valid Credentials?", valid_credentials)

        # Redirect user to dashboard if correct login data.
        if valid_credentials:
            return redirect(url_for("dashboard"))

    return render_template("login.html", title="PyMart Intranet System | Login", page="login", form_errors=errors)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", title="PyMart Intranet System | Dashboard", page="dashboard")


def hash_password(password: str) -> str:
    # Generate random salt that is 40 characters long.
    salt = os.urandom(20).hex()
    print("Salt:", salt)

    to_hash = salt + password
    print("Salt + PW:", to_hash)
    to_hash = to_hash.encode("utf-8")
    print("Encoded S+P:", to_hash)

    password_hash = hashlib.sha256(to_hash).hexdigest()
    print("HASH:", password_hash)

    # Prepend salt to password_hash for storage.
    salt_and_password_hash = salt + password_hash

    return salt_and_password_hash


def authenticate(plaintext_password: str, stored: str) -> bool:
    salt_length = 40

    # Get salt and password hash from stored salt + hashed password.
    salt = stored[:salt_length]
    password_hash = stored[salt_length:]

    # Hash salt + plaintext password from user input.
    to_hash = salt + plaintext_password
    to_hash = to_hash.encode("utf-8")
    attempt_hash = hashlib.sha256(to_hash).hexdigest()

    return attempt_hash == password_hash

if __name__ == "__main__":
    app.run(debug=True)