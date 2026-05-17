# Gerenciador de Planos de Aula

Projeto simples para criação, edição e gerenciamento de planos de aula.

## Tecnologias utilizadas

- Python 3.x
- Flask — microframework web
- Jinja2 — templates (via Flask)
- SQLAlchemy — ORM para persistência
- SQLite — banco de dados leve (arquivo `meubanco.db`)
- Flask-Bcrypt — hashing de senhas
- python-dotenv — carregamento de variáveis de ambiente a partir de `.env`
- Tailwind CSS (via CDN) — estilos
- JavaScript (Vanilla) — lógica do frontend
- Lucide Icons (via CDN) — ícones
- OpenRouter (opcional) — integração para gerar recomendações de IA (requere chave `OPENROUTER_API_KEY`)

## Estrutura do projeto

- `main.py`: Ponto de entrada da aplicação. Carrega variáveis de ambiente, cria a instância do Flask, cria as tabelas do banco (SQLAlchemy) e inicia a aplicação.

- `models.py`: Define os modelos de dados com SQLAlchemy (`User`, `Plan`) e a conexão com o banco SQLite (`meubanco.db`). Também expõe a sessão (`session`) para uso pelas views.

- `views.py`: Define as rotas da aplicação (autenticação, cadastro, dashboard) e APIs REST (`/api/planos`, `/api/ia-recommendations`). Contém a lógica de criação/edição/exclusão de planos e integração com o serviço de IA.

- `templates/`: Pasta com os arquivos HTML (templates Jinja2):
  - `login.html` — tela de login.
  - `cadastro.html` — formulário de criação de conta.
  - `dashboard.html` — painel principal para listar, criar e editar planos de aula.

- `static/`: Arquivos estáticos (CSS, JS, imagens):
  - `style.css` — estilos personalizados e import do Tailwind CSS.
  - `dashboard.js` — lógica do frontend para listagem, paginação, criação/edição/exclusão de planos e chamada das APIs.

## Observações importantes

- Variáveis de ambiente esperadas:
  - `FLASK_SECRET_KEY` — chave secreta do Flask (sessões).
  - `OPENROUTER_API_KEY` — chave para usar o endpoint de recomendações de IA (opcional, usado por `/api/ia-recommendations`).

- Dependências principais (sugeridas para `requirements.txt`):
```
Flask
SQLAlchemy
Flask-Bcrypt
python-dotenv
```

- Banco de dados: o projeto usa SQLite por padrão (`PlanAula.db`), criado automaticamente por SQLAlchemy.

- Executar localmente (exemplo):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# definir variáveis no .env (FLASK_SECRET_KEY, opcionalmente OPENROUTER_API_KEY)
python main.py
```
ou

```
No arquivo main.py, basta apenas clicar para funcionar o pyhon file, e no seu localhost na porta definida (5000 por padrão), basta apenas usar o aplicativo

Para visualização do banco foi utilizado o aplicativo DBBrowser


```

## Contato 

OBS: caso ocorra erros na geração da IA, mandar email para gustavojonathan048@gmail.com, para verificação da chave de api e/ou ativação da mesma
---

README gerado pelo assistente
Video explicativo: https://youtu.be/0EOu5fcEmFE?si=OUt63L93IY9Tr-hH
