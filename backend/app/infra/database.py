from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexão para o SQLite
DATABASE_URL = "sqlite:///./biblioteca.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Função para obter uma sessão do banco de dados (será usada para injeção de dependência)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()