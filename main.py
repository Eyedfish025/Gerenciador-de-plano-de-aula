import os

from dotenv import load_dotenv
from flask import Flask

import models
import views

# carrega as variáveis de ambiente do arquivo .env para configuração da aplicação.
load_dotenv()

# Cria a instância principal do aplicativo Flask.
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# Cria as tabelas do banco de dados caso elas não existam
models.Base.metadata.create_all(bind=models.dbaula)

if __name__ == "__main__":
    # Roda a aplicação quando esse arquivo for executado diretamente.
    views.app.run()
