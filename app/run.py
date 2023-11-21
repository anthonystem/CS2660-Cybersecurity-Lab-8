from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, Lab 8!"

if __name__ == "__main__":
    app.run(debug=True)