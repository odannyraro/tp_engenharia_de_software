from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# 1. ENGINE DE CONEXÃO
# O engine é criado uma vez, usando a URL do arquivo de configuração.
# O argumento `connect_args` é específico e necessário para o SQLite.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 2. FÁBRICA DE SESSÕES
# SessionLocal é uma classe. Instâncias desta classe serão as sessões do banco de dados.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. BASE DECLARATIVA
# Usaremos esta classe Base como herança para todos os nossos modelos ORM (SQLAlchemy).
Base = declarative_base()

# 4. DEPENDÊNCIA DE SESSÃO
# Função geradora que cria uma sessão para uma requisição,
# a disponibiliza e garante que ela seja fechada ao final.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()