from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

@app.route("/")
def index():
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

if __name__ == "__main__":
    app.run(debug=True)