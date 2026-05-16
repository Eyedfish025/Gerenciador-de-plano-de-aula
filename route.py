from main import app
from flask import render_template, request, redirect
from models import session, User
from flask_bcrypt import generate_password_hash, check_password_hash
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

@app.route("/cadastra", methods=["POST"])
def cadastra():
    email = request.form.get("email")
    nome = request.form.get("nome")
    senha = request.form.get("senha")
    senha = generate_password_hash(senha).decode('utf-8')

    novo_usuario = User(email=email, nome=nome, senha=senha)
    session.add(novo_usuario)
    session.commit()

    return redirect('/')