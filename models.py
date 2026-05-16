from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

dbaula = create_engine("sqlite:///meubanco.db")

Session = sessionmaker(bind=dbaula)

session = Session()

Base = declarative_base()

# tabelas

class User(Base):
    __tablename__ = "users"
    email = Column("Email", String(100), primary_key=True)
    nome = Column("Nome", String(100))
    senha = Column("Senha", String(128))

    planos = relationship("Plan", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, email, nome, senha):
        self.nome = nome
        self.email = email
        self.senha = senha

class Plan(Base):
    __tablename__ = "planos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200))
    objetivo = Column(String(1000))
    ementa = Column(String(1000))
    dataPrevista = Column(String(10))
    disciplina = Column(String(100))
    conteudos = Column(String(1000))
    recursos = Column(String(1000))
    tags = Column(String(300))
    user_email = Column(String(100), ForeignKey("users.Email"), nullable=False)

    user = relationship("User", back_populates="planos")

    def __init__(self, titulo, objetivo, ementa, dataPrevista, disciplina, conteudos, recursos, tags, user_email):
        self.titulo = titulo
        self.objetivo = objetivo
        self.ementa = ementa
        self.dataPrevista = dataPrevista
        self.disciplina = disciplina
        self.conteudos = conteudos
        self.recursos = recursos
        self.tags = tags
        self.user_email = user_email

Base.metadata.create_all(bind=dbaula)