from main import app
from flask import render_template
#rotas
@app.route("/")

def homepage():
    return render_template("login.html")

@app.route("/dashboard")

def dashboard():
    return render_template("dashboard.html")


@app.route("/cadastro")

def cadastro():
    return  render_template("cadastro.html")