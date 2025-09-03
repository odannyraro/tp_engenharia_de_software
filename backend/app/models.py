from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base

db = create_engine("sqlite:///banco.db") # conexão com o db

Base = declarative_base() # base do db

class Usuario(Base):
    __tablename__= "usuarios"

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

class Evento(Base):
    __tablename__= "eventos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    sigla = Column("sigla", String)
    descricao = Column("descricao", String)
    site = Column("site", String)

    def __init__(self, nome, sigla=None, descricao=None, site=None):
        self.nome = nome
        self.sigla = sigla
        self.descricao = descricao
        self.site = site

class EdicaoEvento(Base):
    __tablename__= "edicoes"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    ano = Column("ano", Integer, nullable=False)
    local = Column("local", String)
    id_evento = Column("id_evento", ForeignKey("eventos.id"))

    def __init__(self, ano, id_evento, local=None):
        self.ano = ano
        self.local = local
        self.id_evento = id_evento

class Artigo(Base):
    __tablename__ = 'artigos'

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    ano = Column(Integer, nullable=True)
    doi = Column(String, unique=True, index=True, nullable=True)
    caminho_pdf = Column(String, nullable=True)
    id_edicao = Column(Integer, nullable=False)
    
    # Metadados de publicação
    journal = Column(String, nullable=True)
    volume = Column(String, nullable=True)
    numero = Column(String, nullable=True)
    paginas = Column(String, nullable=True)
    publicador = Column(String, nullable=True)

    def __init__(self, titulo, id_edicao, ano=None, doi=None, caminho_pdf=None, journal=None, volume=None, numero=None, paginas=None, publicador=None):
        self.titulo = titulo
        self.ano = ano
        self.doi = doi
        self.caminho_pdf = caminho_pdf
        self.id_edicao = id_edicao
        self.journal = journal
        self.volume = volume
        self.numero = numero
        self.paginas = paginas
        self.publicador = publicador