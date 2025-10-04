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
    entidade_promotora = Column("entidade_promotora", String, nullable=True)

    def __init__(self, nome, sigla=None, descricao=None, site=None, entidade_promotora=None):
        self.nome = nome
        self.sigla = sigla
        self.descricao = descricao
        self.site = site
        self.entidade_promotora = entidade_promotora

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
    titulo = Column(String, index=True, nullable=True)
    # autores: string with full names separated by ' and ' (e.g. 'Davi Freitas and Breno Miranda')
    autores = Column(String, nullable=False)
    nome_evento = Column(String, nullable=False)
    ano = Column(Integer, nullable=True)
    pagina_inicial = Column(Integer, nullable=True)
    pagina_final = Column(Integer, nullable=True)
    caminho_pdf = Column(String, nullable=True)
    # Opcional: campos para referência em proceedings/collections
    booktitle = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    # Local (localização/venue) opcional do artigo na edição
    location = Column(String, nullable=True)
    # ligação para edição (id da tabela edicoes)
    id_edicao = Column(Integer, nullable=True)

    def __init__(self, titulo: str, autores: str, nome_evento: str, ano: int = None, pagina_inicial: int = None, pagina_final: int = None, caminho_pdf: str = None, booktitle: str = None, publisher: str = None, location: str = None, id_edicao: int = None):
        self.titulo = titulo
        self.autores = autores
        self.nome_evento = nome_evento
        self.ano = ano
        self.pagina_inicial = pagina_inicial
        self.pagina_final = pagina_final
        self.caminho_pdf = caminho_pdf
        self.booktitle = booktitle
        self.publisher = publisher
        self.location = location
        self.id_edicao = id_edicao

class Subscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=False)

    def __init__(self, nome, email):
        self.nome = nome
        self.email = email