from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils import ChoiceType

db = create_engine("sqlite:///banco.db") # conexão com o db

Base = declarative_base() # base do db

class Usuario(Base):
    __tablename__="usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    email = Column("email", String, nullable=False)
    senha = Column("senha", String)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, nome, email, senha, admin= False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.admin = admin