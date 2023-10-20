from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/name/<name>")
def show_name(name):
    return render_template("name.html", name=name)
