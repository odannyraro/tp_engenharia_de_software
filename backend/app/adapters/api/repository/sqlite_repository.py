from typing import List
from sqlalchemy.orm import Session
from app.domain.entities.artigo import Artigo
from app.domain.repositories.i_artigo_repository import IArtigoRepository
# Importe aqui o seu modelo SQLAlchemy se for diferente da entidade Pydantic

# Neste exemplo, vamos assumir que o modelo SQLAlchemy é o mesmo da entidade
# Em um projeto real, você poderia ter um modelo separado e fazer a conversão aqui

class SQLiteArtigoRepository(IArtigoRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def find_by_titulo(self, titulo: str) -> List[Artigo]:
        # Aqui iria a lógica de consulta com SQLAlchemy
        # Exemplo simplificado:
        # return self.db_session.query(ArtigoModel).filter(ArtigoModel.titulo.contains(titulo)).all()
        print(f"Buscando no SQLite por artigos com título: {titulo}")
        # Retorno fake para exemplo:
        return [Artigo(id=1, titulo="Exemplo de Artigo sobre Clean Architecture", ano=2025)]

    def save(self, artigo: Artigo) -> Artigo:
        # Lógica para salvar com self.db_session.add() e .commit()
        pass