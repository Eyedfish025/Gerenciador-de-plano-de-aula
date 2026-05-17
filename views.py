import json
import os
import urllib.error
import urllib.request

from flask import flash, jsonify, redirect, render_template, request
from flask import session as flask_session
from flask_bcrypt import check_password_hash, generate_password_hash

from main import app
from models import Plan, User
from models import session as db_session


# Rotas da aplicação e APIs REST.
@app.route("/")
def homepage():
    # Renderiza a página de login inicial.
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    # Autentica o usuário e inicia a sessão caso as credenciais sejam válidas.

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
    # Encerra a sessão do usuário e redireciona para a tela de login.
    flask_session.clear()
    return redirect("/")


@app.route("/dashboard")
def dashboard():
    # Mostra o painel de gerenciamento de planos apenas para usuários autenticados.
    if "user_email" not in flask_session:
        return redirect("/")
    return render_template("dashboard.html", user_name=flask_session.get("user_name"))


@app.route("/cadastro")
def cadastro():
    # Renderiza o formulário de cadastro de novo usuário.
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
    # Retorna os planos do usuário autenticado em formato JSON.
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


@app.route("/api/ia-recommendations", methods=["POST"])
def ia_recommendations():
    # Recebe título, disciplina e ementa, consulta a IA e retorna recomendações.
    if "user_email" not in flask_session:
        return jsonify({"error": "Usuário não autenticado."}), 401

    data = request.get_json() or {}
    titulo = (data.get("titulo") or "").strip()
    disciplina = (data.get("disciplina") or "").strip()
    ementa = (data.get("ementa") or "").strip()

    if not titulo or not disciplina or not ementa:
        return jsonify({"error": "Título, disciplina e ementa são obrigatórios."}), 400

    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        return jsonify({"error": "Chave OPENROUTER_API_KEY não configurada."}), 500

    prompt = (
        "Você é um assistente para professores. Use o título, disciplina e ementa para gerar sugestões de conteúdos complementares, recursos, tópicos relacionados e 3 tags recomendadas. "
        "Responda apenas com um JSON válido, sem markdown e sem texto adicional. "
        'O formato deve ser exatamente: {"conteudos":"...","recursos":"...","relatedTopics":"...","tags":["tag1","tag2","tag3"]}. '
        f"Título: {titulo}\nDisciplina: {disciplina}\nEmenta: {ementa}"
    )

    payload = {
        "model": "openai/gpt-5.2",
        "messages": [
            {
                "role": "system",
                "content": "Você é um assistente de criação de planos de aula.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.0,
        "max_tokens": 400,
    }

    def parse_json_text(text):
        # Tenta extrair e desserializar JSON de uma string de resposta da IA.
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            import re

            start = text.find("{")
            if start == -1:
                raise

            # Tenta extrair o primeiro objeto JSON completo a partir da primeira chave.
            matches = list(re.finditer(r"\}", text[start:]))
            for match in reversed(matches):
                candidate = text[start : start + match.end()]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue

            # Última tentativa: extrai qualquer conteúdo entre chaves e parseia.
            match = re.search(r"\{.*\}", text[start:], re.DOTALL)
            if match:
                return json.loads(match.group(0))

            raise

    try:
        request_data = json.dumps(payload).encode("utf-8")
        request_obj = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=request_data,
            headers={
                "Authorization": f"Bearer {openrouter_api_key}",
                "OpenRouter-Api-Key": openrouter_api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(request_obj, timeout=15) as response:
            response_text = response.read().decode("utf-8")
            completion = json.loads(response_text)

        if "choices" not in completion or not completion["choices"]:
            return jsonify({"error": f"Resposta inesperada da IA: {completion}"}), 500

        content = completion["choices"][0]["message"]["content"]

        try:
            result = parse_json_text(content)
        except json.JSONDecodeError as parse_exc:
            return (
                jsonify(
                    {
                        "error": f"Falha ao analisar resposta da IA: {str(parse_exc)}",
                        "raw": content,
                    }
                ),
                500,
            )

        tags = result.get("tags", [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(",") if tag.strip()]

        return jsonify(
            {
                "conteudos": result.get("conteudos", ""),
                "recursos": result.get("recursos", ""),
                "relatedTopics": result.get("relatedTopics", ""),
                "tags": tags,
            }
        )
    except urllib.error.HTTPError as http_err:
        try:
            error_body = http_err.read().decode("utf-8")
            error_json = json.loads(error_body)
            message = error_json.get("error", {}).get("message", str(http_err))
        except Exception:
            message = str(http_err)
        return jsonify({"error": f"Falha ao obter recomendações de IA: {message}"}), 500
    except Exception as exc:
        return (
            jsonify({"error": f"Falha ao obter recomendações de IA: {str(exc)}"}),
            500,
        )


@app.route("/api/planos", methods=["POST"])
def create_plano():
    # Cria um novo plano de aula associado ao usuário atual.
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
    # Atualiza um plano existente se pertencer ao usuário autenticado.
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
    # Exclui um plano existente se ele pertencer ao usuário atual.
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
