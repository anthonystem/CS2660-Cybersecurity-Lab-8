from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", title="PyMart Intranet System | Welcome", page="landing")

@app.route("/login")
def login():
    return render_template("login.html", title="PyMart Intranet System | Login", page="login")

if __name__ == "__main__":
    app.run(debug=True)