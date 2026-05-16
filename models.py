from sqlalchemy import create_engine, Column, String, Integer,ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

dbaula = create_engine("sqlite:///meubanco.db")

Session = sessionmaker(bind=dbaula)

session = Session()

Base = declarative_base()

#tabelas
class User (Base):
    __tablename__ = "users"
    email = Column("Email", String(100), primary_key=True)
    nome = Column ("Nome", String(100))
    senha = Column("Senha", Integer)

    def __init__(self,email,nome,senha):
        self.nome = nome
        self.email = email
        self.senha = senha


#salvar o plano de aula?
#

Base.metadata.create_all(bind=dbaula)