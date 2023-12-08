import authentication
from database import Database
from flask import Flask, render_template, redirect, request, session, url_for
import sqlite3
import config

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config")
app.secret_key = app.config['SECRET_KEY']

@app.route("/")
@app.route("/index")
def index():
    # Render dashboard if session is already set.
    if session.get("user_id", None) is not None:
        return redirect(url_for("dashboard"))
    
    return render_template("index.html", title="PyMart Intranet System | Welcome", page="landing")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    # Render dashboard if session is already set.
    if session.get("user_id", None) is not None:
        return redirect(url_for("dashboard"))
    
    errors = []
    if request.method == "POST":
        ### Get login form data.
        username = request.form.get("username")
        password = request.form.get("password")

        ### Check if input credentials are in the database.
        connection = sqlite3.connect(config.DATABASE_FILE)
        cursor = connection.cursor()

        cursor.execute("SELECT password FROM Users WHERE username = ?", (username,))
        stored_password = cursor.fetchone()

        if stored_password is None:
            valid_credentials = False
        else:   
            valid_credentials = authentication.authenticate(password, stored_password[0])

        ### Handle valid and invalid credentials.
        # Redirect user to dashboard and initialize session if correct login data.
        # Otherwise, append incorrect username/password error and re-render login.
        if valid_credentials:
            # Get user_id and create session with user_id and username; redirect to dashboard after.
            cursor.execute("SELECT user_id FROM Users WHERE username = ?", (username,))
            user_id = cursor.fetchone()[0]
            session["user_id"] = user_id
            session
            cursor.close()
            connection.close()
            return redirect(url_for("dashboard"))
        
        cursor.close()
        connection.close()

        errors.append("Incorrect username or password. Please try again.")

    return render_template("login.html", title="PyMart Intranet System | Login", page="login", error_alerts=errors)


@app.route("/register", methods=["GET", "POST"])
def register():
    # Render dashboard if session is already set.
    if session.get("user_id", None) is not None:
        return redirect(url_for("dashboard"))
    
    errors = []
    if request.method == "POST":
        new_username = request.form.get("new-username")
        new_password = request.form.get("new-password")
        password_confirmation = request.form.get("password-confirmation")

        valid_credentials = True
        # Check password matches confirmation password.
        if new_password == password_confirmation:
            # Check if username exists already.
            if authentication.username_exists(new_username):
                errors.append("Username is already taken. Please try again.")
                valid_credentials = False
            # Check that username meets requirements.
            if not authentication.validate_username(new_username):
                errors.append("Username must be at least 3 characters and at most 16 characters long. Please try again.")
                valid_credentials = False
            # Check that password meets requirements described in password policy.
            if not authentication.validate_password(new_password):
                errors.append("The password you provided does not meet the requirements set by the password policy. Please try again.")
                valid_credentials = False
        else:
            errors.append("Passwords do not match. Please try again.")
            valid_credentials = False

        # Add user to database (default access level to "STANDARD") if valid credentials.
        if valid_credentials:
            # Hash password and insert information into database.
            new_password = authentication.hash_password(new_password)

            connection = sqlite3.connect(config.DATABASE_FILE)
            cursor = connection.cursor()

            cursor.execute("INSERT INTO Users (username, password, access_level) VALUES (?, ?, ?)", (new_username, new_password, "STANDARD"))
            connection.commit()
            cursor.close()
            connection.close()

            # Redirect to login.
            return redirect(url_for("login"))

    return render_template("register.html", title="PyMart Intranet System | Register", page="register", alert_errors=errors)


@app.route("/dashboard")
def dashboard():
    # Redirect to index if user is not logged in.
    if session.get("user_id", None) is None:
        return redirect(url_for("index"))
    
    return render_template("dashboard.html", title="PyMart Intranet System | Dashboard", page="dashboard")


if __name__ == "__main__":
    app.run(debug=True)