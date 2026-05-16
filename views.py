from flask import flash, jsonify, redirect, render_template, request
from flask import session as flask_session
from flask_bcrypt import check_password_hash, generate_password_hash

from main import app
from models import Plan, User
from models import session as db_session


# rotas
@app.route("/")
def homepage():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    login_mail = request.form.get("login-mail")
    login_senha = request.form.get("login-senha")
    if login_mail and login_senha:
        user = db_session.query(User).filter_by(email=login_mail).first()
        if user and check_password_hash(user.senha, login_senha):
            flask_session["user_email"] = user.email
            flask_session["user_name"] = user.nome
            return redirect("/dashboard")

    flash("Email ou senha incorretos.")
    return redirect("/")


@app.route("/logout")
def logout():
    flask_session.clear()
    return redirect("/")


@app.route("/dashboard")
def dashboard():
    if "user_email" not in flask_session:
        return redirect("/")
    return render_template("dashboard.html", user_name=flask_session.get("user_name"))


@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@app.route("/cadastra", methods=["POST"])
def cadastra():
    email = request.form.get("email")
    nome = request.form.get("nome")
    senha = request.form.get("senha")
    senha = generate_password_hash(senha).decode("utf-8")

    novo_usuario = User(email=email, nome=nome, senha=senha)
    db_session.add(novo_usuario)
    db_session.commit()

    return redirect("/")


@app.route("/api/planos", methods=["GET"])
def get_planos():
    if "user_email" not in flask_session:
        return jsonify({"error": "Usuário não autenticado."}), 401

    planos = (
        db_session.query(Plan)
        .filter_by(user_email=flask_session["user_email"])
        .order_by(Plan.id.desc())
        .all()
    )
    return jsonify(
        {
            "planos": [
                {
                    "id": plano.id,
                    "titulo": plano.titulo,
                    "objetivo": plano.objetivo,
                    "ementa": plano.ementa,
                    "dataPrevista": plano.dataPrevista,
                    "disciplina": plano.disciplina,
                    "conteudos": plano.conteudos,
                    "recursos": plano.recursos,
                    "tags": plano.tags or "",
                }
                for plano in planos
            ]
        }
    )


@app.route("/api/planos", methods=["POST"])
def create_plano():
    if "user_email" not in flask_session:
        return jsonify({"error": "Usuário não autenticado."}), 401

    data = request.get_json() or {}
    novo_plano = Plan(
        titulo=data.get("titulo", ""),
        objetivo=data.get("objetivo", ""),
        ementa=data.get("ementa", ""),
        dataPrevista=data.get("dataPrevista", ""),
        disciplina=data.get("disciplina", ""),
        conteudos=data.get("conteudos", ""),
        recursos=data.get("recursos", ""),
        tags=data.get("tags", ""),
        user_email=flask_session["user_email"],
    )

    db_session.add(novo_plano)
    db_session.commit()
    return jsonify({"id": novo_plano.id}), 201


@app.route("/api/planos/<int:plano_id>", methods=["PUT"])
def update_plano(plano_id):
    if "user_email" not in flask_session:
        return jsonify({"error": "Usuário não autenticado."}), 401

    plano = (
        db_session.query(Plan)
        .filter_by(id=plano_id, user_email=flask_session["user_email"])
        .first()
    )
    if not plano:
        return jsonify({"error": "Plano não encontrado."}), 404

    data = request.get_json() or {}
    plano.titulo = data.get("titulo", plano.titulo)
    plano.objetivo = data.get("objetivo", plano.objetivo)
    plano.ementa = data.get("ementa", plano.ementa)
    plano.dataPrevista = data.get("dataPrevista", plano.dataPrevista)
    plano.disciplina = data.get("disciplina", plano.disciplina)
    plano.conteudos = data.get("conteudos", plano.conteudos)
    plano.recursos = data.get("recursos", plano.recursos)
    plano.tags = data.get("tags", plano.tags)

    db_session.commit()
    return jsonify({"success": True})


@app.route("/api/planos/<int:plano_id>", methods=["DELETE"])
def delete_plano(plano_id):
    if "user_email" not in flask_session:
        return jsonify({"error": "Usuário não autenticado."}), 401

    plano = (
        db_session.query(Plan)
        .filter_by(id=plano_id, user_email=flask_session["user_email"])
        .first()
    )
    if not plano:
        return jsonify({"error": "Plano não encontrado."}), 404

    db_session.delete(plano)
    db_session.commit()
    return jsonify({"success": True})
