import json
import logging
import os
import urllib.error
import urllib.request

from flask import flash, jsonify, redirect, render_template, request
from flask import session as flask_session
from flask_bcrypt import check_password_hash, generate_password_hash

from main import app
from models import Plan, User
from models import session as db_session

logger = logging.getLogger(__name__)


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
    logger.info(
        "IA prompt gerado para usuário %s: %s", flask_session.get("user_email"), prompt
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
        "max_tokens": 1000,
    }

    def parse_json_text(text):
        # Tenta extrair e desserializar JSON de uma string de resposta da IA.
        import re

        cleaned = text.strip()
        cleaned = re.sub(r"```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^.*?\{", "{", cleaned, flags=re.DOTALL)

        def extract_json_object(source):
            depth = 0
            in_string = False
            escape = False
            start_index = source.find("{")
            if start_index == -1:
                return None

            for index in range(start_index, len(source)):
                char = source[index]
                if char == "\\" and not escape:
                    escape = True
                    continue
                if char == '"' and not escape:
                    in_string = not in_string
                if not in_string:
                    if char == "{":
                        depth += 1
                    elif char == "}":
                        depth -= 1
                        if depth == 0:
                            return source[start_index : index + 1]
                if escape:
                    escape = False
            return None

        def escape_raw_newlines(source):
            escaped = []
            in_string = False
            escape = False
            for char in source:
                if char == "\\" and not escape:
                    escape = True
                    escaped.append(char)
                    continue
                if char == '"' and not escape:
                    in_string = not in_string
                    escaped.append(char)
                elif in_string and char == "\n":
                    escaped.append("\\n")
                elif in_string and char == "\r":
                    escaped.append("\\r")
                elif in_string and char == "\t":
                    escaped.append("\\t")
                else:
                    escaped.append(char)
                if escape and char != "\\":
                    escape = False
            return "".join(escaped)

        def sanitize_candidate(source):
            source = source.strip()
            if "}" in source:
                source = source[: source.rfind("}") + 1]
            source = source.replace("\r", "\\r").replace("\n", "\\n")
            return source

        def try_load_json(source):
            source = source.strip()
            if not source:
                raise ValueError("Nenhum JSON encontrado")
            if not source.endswith("}"):
                source = source[: source.rfind("}") + 1]
            while source:
                try:
                    return json.loads(source)
                except json.JSONDecodeError as exc:
                    if (
                        "Unterminated string" in str(exc)
                        or "Expecting property name" in str(exc)
                        or "Extra data" in str(exc)
                    ):
                        comma_index = source.rfind(",")
                        if comma_index == -1:
                            raise exc
                        source = source[:comma_index] + "}"
                        continue
                    raise exc

        candidate = extract_json_object(cleaned)
        if candidate is None:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            candidate = match.group(0) if match else cleaned

        candidate = escape_raw_newlines(candidate)
        candidate = sanitize_candidate(candidate)

        try:
            return try_load_json(candidate)
        except json.JSONDecodeError as exc:
            alt_candidate = candidate.replace("'", '"')
            return try_load_json(alt_candidate)

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

        logger.info(
            "Resposta bruta da IA para usuário %s: %s",
            flask_session.get("user_email"),
            response_text,
        )
        if "choices" not in completion or not completion["choices"]:
            logger.warning("Resposta inesperada da IA: %s", completion)
            return jsonify({"error": f"Resposta inesperada da IA: {completion}"}), 500

        choice = completion["choices"][0]
        message = choice.get("message") if isinstance(choice, dict) else None
        content = message.get("content") if isinstance(message, dict) else ""
        logger.info("Conteúdo extraído da IA: %s", content)

        if not content:
            logger.error("Conteúdo da IA ausente ou vazio: %s", choice)
            return (
                jsonify(
                    {
                        "error": "Conteúdo da IA ausente ou vazio.",
                        "raw": completion,
                    }
                ),
                500,
            )

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

        if result is None or not isinstance(result, dict):
            logger.error("Resposta parseada inválida da IA: %s", result)
            return (
                jsonify(
                    {
                        "error": "Resposta da IA não veio no formato esperado.",
                        "raw": content,
                    }
                ),
                500,
            )

        # 1. Trata as tags (mantém o seu comportamento original)
        tags = result.get("tags", [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # 2. Nova função auxiliar interna para garantir que o front-end SEMPRE receba uma String
        def forcar_string(valor):
            if valor is None:
                return ""
            if isinstance(valor, list):
                # Se a IA enviou uma lista de itens, junta tudo quebrando linha
                return "\n".join(str(item) for item in valor)
            if isinstance(valor, dict):
                # Se a IA inventou um objeto/dicionário, transforma em texto formatado
                return json.dumps(valor, ensure_ascii=False, indent=2)
            # Se já for string ou qualquer outro tipo, converte para string pura
            return str(valor)

        # 3. Limpa e garante o tipo string para os três campos textuais
        conteudos_limpo = forcar_string(result.get("conteudos", ""))
        recursos_limpo = forcar_string(result.get("recursos", ""))
        related_topics_limpo = forcar_string(result.get("relatedTopics", ""))

        # 4. Retorna com segurança para o front-end
        return jsonify(
            {
                "conteudos": conteudos_limpo,
                "recursos": recursos_limpo,
                "relatedTopics": related_topics_limpo,
                "tags": tags,
            }
        )

    except urllib.error.HTTPError as http_err:
        try:
            error_body = http_err.read().decode("utf-8")
            error_json = None
            try:
                error_json = json.loads(error_body)
            except json.JSONDecodeError:
                pass

            if isinstance(error_json, dict):
                message = error_json.get("error", {})
                if isinstance(message, dict):
                    message = message.get("message")
                if not message:
                    message = error_json.get("message")
                if not message:
                    message = error_json.get("detail")
            else:
                message = None

            if not message:
                message = str(http_err)
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
