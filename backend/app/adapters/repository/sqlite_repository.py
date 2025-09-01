# File: backend/app/adapters/repositories/sqlite_artigo_repository.py

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String

# Importações da Arquitetura Limpa
from app.domain.entities.artigo import Artigo as ArtigoEntity
from app.domain.repositories.i_artigo_repository import IArtigoRepository
from app.infra.database import Base

# 1. MODELO DA TABELA (SQLAlchemy)
# Esta classe define a estrutura da tabela 'artigos' no banco de dados,
# espelhando todos os campos da sua entidade 'Artigo'.
class ArtigoModel(Base):
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


# 2. IMPLEMENTAÇÃO DO REPOSITÓRIO
# Esta classe implementa a lógica para interagir com a tabela 'artigos'.
class SQLiteArtigoRepository(IArtigoRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, model: ArtigoModel) -> ArtigoEntity:
        """Converte um modelo SQLAlchemy para uma entidade de domínio Pydantic."""
        return ArtigoEntity.from_orm(model)

    def save(self, artigo: ArtigoEntity) -> ArtigoEntity:
        """
        Salva um novo artigo. O mapeamento aqui inclui todos os campos
        da entidade para o modelo do banco de dados.
        """
        artigo_model = ArtigoModel(
            titulo=artigo.titulo,
            ano=artigo.ano,
            doi=artigo.doi,
            caminho_pdf=artigo.caminho_pdf,
            id_edicao=artigo.id_edicao,
            journal=artigo.journal,
            volume=artigo.volume,
            numero=artigo.numero,
            paginas=artigo.paginas,
            publicador=artigo.publicador
        )
        self.db_session.add(artigo_model)
        self.db_session.commit()
        self.db_session.refresh(artigo_model)
        return self._to_entity(artigo_model)

    def find_by_id(self, artigo_id: int) -> Optional[ArtigoEntity]:
        model = self.db_session.query(ArtigoModel).filter(ArtigoModel.id == artigo_id).first()
        return self._to_entity(model) if model else None

    def find_by_titulo(self, titulo: str) -> List[ArtigoEntity]:
        query_result = self.db_session.query(ArtigoModel).filter(ArtigoModel.titulo.contains(titulo)).all()
        return [self._to_entity(artigo) for artigo in query_result]

    def find_by_autor_id(self, autor_id: int) -> List[ArtigoEntity]:
        # A lógica real aqui exigiria um relacionamento/join com a tabela de autores.
        print(f"Placeholder: Lógica para buscar artigos do autor {autor_id} a ser implementada.")
        return []

    def find_by_edicao_id(self, edicao_id: int) -> List[ArtigoEntity]:
        query_result = self.db_session.query(ArtigoModel).filter(ArtigoModel.id_edicao == edicao_id).all()
        return [self._to_entity(artigo) for artigo in query_result]

    def find_all(self) -> List[ArtigoEntity]:
        query_result = self.db_session.query(ArtigoModel).all()
        return [self._to_entity(artigo) for artigo in query_result]

    def delete(self, artigo_id: int) -> None:
        model = self.db_session.query(ArtigoModel).filter(ArtigoModel.id == artigo_id).first()
        if model:
            self.db_session.delete(model)
            self.db_session.commit()