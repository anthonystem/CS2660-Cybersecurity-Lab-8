import authentication
from database import Database
from flask import Flask, render_template, redirect, request, session, url_for
import sqlite3
import config

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
        ### Get login form data.
        username = request.form.get("username")
        password = request.form.get("password")
        print("Username:", username)
        print("Password:", password)

        ### Check if input credentials are in the database.
        Database.setup(test_mode=True)
        connection = sqlite3.connect(config.DATABASE_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM Users WHERE username = ?", (username,))
        stored_password = cursor.fetchone()
        if stored_password is None:
            print("Could not find username and password.")
            valid_credentials = False
        else:   
            valid_credentials = authentication.authenticate(password, stored_password[0])

        ### Handle valid and invalid credentials.
        print("Valid Credentials?", valid_credentials)

        # Redirect user to dashboard if correct login data; otherwise, append error and render login.
        if valid_credentials:
            return redirect(url_for("dashboard"))
        
        errors.append("Incorrect username or password. Please try again.")

    return render_template("login.html", title="PyMart Intranet System | Login", page="login", form_errors=errors)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", title="PyMart Intranet System | Dashboard", page="dashboard")

if __name__ == "__main__":
    app.run(debug=True)