import authentication
from flask import Flask, flash, render_template, redirect, request, session, url_for
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
    session.clear()
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    successes = []
    errors = []
    # Render dashboard if session is already set.
    if session.get("user_id", None) is not None:
        return redirect(url_for("dashboard"))
    
    if session.get("generated_password", None) is not None:
        successes.append(f"Registration successful. Your strong password is \"{session['generated_password']}\". Please log in.")
        session.pop("generated_password")
    elif session.get("registration_success", None) is not None:
        successes.append(f"Registration successful. Please log in.")
        session.pop("registration_success")

    # Start session to track login attempts if not already started.
    if session.get("login_attempts", None) is None:
        session["current_login_attempt_username"] = None
        session["previous_login_attempt_username"] = None
        session["login_attempts"] = 0
    
    if request.method == "POST":
        ### Get login form data.
        username = request.form.get("username")
        password = request.form.get("password")
        session["previous_login_attempt_username"] = session["current_login_attempt_username"]
        session["current_login_attempt_username"] = username

        ### Check if input credentials are in the database.
        connection = sqlite3.connect(config.DATABASE_FILE)
        cursor = connection.cursor()

        valid_credentials = False
        account_exists = False
        try:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM Users WHERE username = ? LIMIT 1)", (username,))     
            if cursor.fetchone()[0] == 1:   
                account_exists = True   
                cursor.execute("SELECT user_id, username, password, access_level, blocked FROM Users WHERE username = ?", (username,))
                user_id, username, stored_password, access_level, blocked = cursor.fetchone()

                # Check if blocked and then authenticate.
                if blocked:
                    errors.append("This account is blocked.")
                    return render_template("login.html", title="PyMart Intranet System | Login", page="login", success_alerts=successes, error_alerts=errors)
                elif stored_password is not None:
                    valid_credentials = authentication.authenticate(password, stored_password)

        except sqlite3.OperationalError:
            errors.append("Error establishing a database connection. Please contact the system administrator.")
            cursor.close()
            connection.close()
            return render_template("login.html", title="PyMart Intranet System | Login", page="login", success_alerts=successes, error_alerts=errors)

        ### Handle valid and invalid credentials.
        # Redirect user to dashboard and initialize session if correct login data.
        # Otherwise, append incorrect username/password error and re-render login.
        if valid_credentials:
            # Get user_id and create session with user_id and username; redirect to dashboard after.
            session["login_attempts"] = 0
            session["user_id"] = user_id
            session["username"] = username
            session["access_level"] = access_level
            cursor.close()
            connection.close()
            return redirect(url_for("dashboard"))
        elif account_exists:
            # Increment failed login attempts if trying the same username otherwise reset.
            if session["current_login_attempt_username"] == session["previous_login_attempt_username"] or \
                session["previous_login_attempt_username"] is None:
                session["login_attempts"] += 1
            else:
                # Change previous login attempt username and reset attempts.
                session["login_attempts"] = 1
                
            if session["login_attempts"] < 3:
                errors.append("Incorrect password. Please try again.")
                errors.append(f"You have {3 - session['login_attempts']} login attempts remaining.")

            if account_exists and session["login_attempts"] >= 3:
                authentication.block_user(session["current_login_attempt_username"])
                errors.append("This account is blocked.")
                session["login_attempts"] = 0
    
        else:
            errors.append("Incorrect username or password. Please try again.")

        cursor.close()
        connection.close()
        

    return render_template("login.html", title="PyMart Intranet System | Login", page="login", success_alerts=successes, error_alerts=errors)


@app.route("/register", methods=["GET", "POST"])
def register():
    # Render dashboard if session is already set.
    if session.get("user_id", None) is not None:
        return redirect(url_for("dashboard"))
    
    errors = []
    if request.method == "POST":
        new_username = request.form.get("new-username")
        generate = request.form.get("generate-password")
        new_password = None

        valid_credentials = True
        # Handle password generator if requested.
        if generate:
            # Generate and hash new password.
            new_password = authentication.generate_strong_password(length=8, max_attempts=1000)
            session["generated_password"] = new_password
            try:
                # Check if username input is valid.
                if not authentication.validate_username(new_username):
                    errors.append("Username must be at least 3 characters and at most 16 characters long. Please try again.")
                    valid_credentials = False

                # Check if username exists already.
                if authentication.username_exists(new_username):
                    errors.append("Username is already taken. Please try again.")
                    valid_credentials = False
   
            except sqlite3.OperationalError:
                errors.append("Error establishing a database connection. Please contact the system administrator.")
                return render_template("register.html", title="PyMart Intranet System | Register", page="register", error_alerts=errors)
        else:
            # Handle normal username/password creation.
            new_password = request.form.get("new-password")
            password_confirmation = request.form.get("password-confirmation")
            try:
                # Check password matches confirmation password.
                if new_password == password_confirmation:
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
            except sqlite3.OperationalError:
                errors.append("Error establishing a database connection. Please contact the system administrator.")
                return render_template("register.html", title="PyMart Intranet System | Register", page="register", error_alerts=errors)

        # Add user to database (default access level to "STANDARD") if valid credentials.
        if valid_credentials:
            # Hash password and insert information into database.
            new_password = authentication.hash_password(new_password)
            connection = sqlite3.connect(config.DATABASE_FILE)
            cursor = connection.cursor()

            # Default access level to STANDARD.
            cursor.execute("INSERT INTO Users (username, password, access_level) VALUES (?, ?, ?)", (new_username, new_password, "STANDARD"))
            connection.commit()

            cursor.close()
            connection.close()

            # Redirect to login.
            session["registration_success"] = True
            return redirect(url_for("login"))

    return render_template("register.html", title="PyMart Intranet System | Register", page="register", error_alerts=errors)


@app.route("/dashboard")
def dashboard():
    # Redirect to index if user is not logged in.
    if session.get("user_id", None) is None:
        return redirect(url_for("index"))
    
    return render_template("dashboard.html", title="PyMart Intranet System | Dashboard", page="dashboard", username=session["username"], access_level=session["access_level"])


@app.route("/time-report")
def time_report():
    # Redirect to index if user is not logged in.
    if session.get("user_id", None) is None:
        return redirect(url_for("index"))
    
    # Check if user has access to view page.
    # >> Access level must be, at least, STANDARD.
    access_level = session["access_level"]
    permission = authentication.has_access_permission(access_level, "STANDARD")
    print(access_level)
    print("Permissions?", permission)

    return render_template("time-report.html", title="PyMart Intranet System | Time Report", page="time-report", has_access=permission, application="Time Report")


@app.route("/inventory")
def inventory():
    # Redirect to index if user is not logged in.
    if session.get("user_id", None) is None:
        return redirect(url_for("index"))
    
    # Check if user has access to view page.
    # >> Access level must be, at least, DEPARTMENT_MANAGER.
    access_level = session["access_level"]
    permission = authentication.has_access_permission(access_level, "DEPARTMENT_MANAGER")
    print(access_level)
    print("Permissions?", permission)
    
    return render_template("time-report.html", title="PyMart Intranet System | Time Report", page="inventory", has_access=permission, application="Inventory")


@app.route("/job-application-manager")
def job_application_manager():
    # Redirect to index if user is not logged in.
    if session.get("user_id", None) is None:
        return redirect(url_for("index"))
    
    # Check if user has access to view page.
    # >> Access level must be, at least, DEPARTMENT_MANAGER.
    access_level = session["access_level"]
    permission = authentication.has_access_permission(access_level, "DEPARTMENT_MANAGER")
    print(access_level)
    print("Permissions?", permission)

    return render_template("time-report.html", title="PyMart Intranet System | Time Report", page="job-application-manager", has_access=permission, application="Job Application Management")

@app.route("/admin")
def admin():
    # Redirect to index if user is not logged in.
    if session.get("user_id", None) is None:
        return redirect(url_for("index"))
    
    # Check if user has access to view page.
    # >> Access level must be ADMINISTRATOR.
    access_level = session["access_level"]
    permission = authentication.has_access_permission(access_level, "ADMIN")
    print(access_level)
    print("Permissions?", permission)

    return render_template("time-report.html", title="PyMart Intranet System | Time Report", page="admin", has_access=permission, application="Admin")


if __name__ == "__main__":
    app.run(debug=True)