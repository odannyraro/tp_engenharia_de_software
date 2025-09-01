# File: backend/app/infrastructure/dependencies.py

from fastapi import Depends
from sqlalchemy.orm import Session

# Importa o provedor de sessão de banco de dados
from .database import get_db

# --- Importa as INTERFACES do domínio ---
from app.domain.repositories.i_artigo_repository import IArtigoRepository
from app.domain.repositories.i_evento_repository import IEventoRepository
# Importe as outras interfaces aqui...

# --- Importa as IMPLEMENTAÇÕES CONCRETAS dos adaptadores ---
from app.adapters.repository.sqlite_repository import SQLiteArtigoRepository
# Para um projeto completo, você criaria e importaria as outras implementações:
# from app.adapters.repositories.sqlite_evento_repository import SQLiteEventoRepository
# ...e assim por diante.

# --- Provedores de Dependência ---

def get_artigo_repository(db: Session = Depends(get_db)) -> IArtigoRepository:
    """
    Provedor de dependência para o repositório de Artigos.

    Esta função será chamada pelo FastAPI sempre que uma rota declarar
    uma dependência do tipo IArtigoRepository.

    Args:
        db (Session): A sessão do banco de dados injetada por `get_db`.

    Returns:
        Uma instância de SQLiteArtigoRepository, que satisfaz o contrato de IArtigoRepository.
    """
    return SQLiteArtigoRepository(db)


# Para completar a arquitetura, você criaria provedores para os outros repositórios.
# Mesmo que as classes concretas ainda não existam, o padrão seria este:

# def get_evento_repository(db: Session = Depends(get_db)) -> IEventoRepository:
#     """Provedor de dependência para o repositório de Eventos."""
#     return SQLiteEventoRepository(db)

# ...e assim por diante para cada repositório da sua aplicação.