# Modelos de banco de dados usando SQLAlchemy para usuários e planos de aula.

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Configura o motor de banco de dados SQLite.
dbaula = create_engine("sqlite:///meubanco.db")

# Cria uma fábrica de sessões e uma instância de sessão para acesso ao banco de dados.
Session = sessionmaker(bind=dbaula)

session = Session()

# Classe base para os modelos de banco de dados.
Base = declarative_base()


class User(Base):
    # Representa um usuário cadastrado no sistema.
    __tablename__ = "users"
    email = Column("Email", String(100), primary_key=True)
    nome = Column("Nome", String(100))
    senha = Column("Senha", String(128))

    # Relacionamento entre usuário e seus planos de aula.
    planos = relationship("Plan", back_populates="user", cascade="all,delete-orphan")

    def __init__(self, email, nome, senha):
        self.nome = nome
        self.email = email
        self.senha = senha


class Plan(Base):
    # Representa um plano de aula criado por um usuário.

    __tablename__ = "planos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200))
    objetivo = Column(String(2000))
    ementa = Column(String(2000))
    dataPrevista = Column(String(10))
    disciplina = Column(String(100))
    conteudos = Column(String(2000))
    recursos = Column(String(2000))
    tags = Column(String(300))
    user_email = Column(String(100), ForeignKey("users.Email"), nullable=False)

    # Define o vínculo do plano ao usuário proprietário.
    user = relationship("User", back_populates="planos")

    def __init__(
        self,
        titulo,
        objetivo,
        ementa,
        dataPrevista,
        disciplina,
        conteudos,
        recursos,
        tags,
        user_email,
    ):
        self.titulo = titulo
        self.objetivo = objetivo
        self.ementa = ementa
        self.dataPrevista = dataPrevista
        self.disciplina = disciplina
        self.conteudos = conteudos
        self.recursos = recursos
        self.tags = tags
        self.user_email = user_email
