from app.infra.database import Base, engine
from app.adapters.repository.sqlite_repository import ArtigoModel
# Importe outros modelos ORM aqui...

def init_db():
    print("Criando tabelas no banco de dados...")
    # O Base.metadata.create_all cria todas as tabelas que herdam de Base
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")

if __name__ == "__main__":
    init_db()