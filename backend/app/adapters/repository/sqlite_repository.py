from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, ForeignKey

# Importações da Arquitetura Limpa
from app.domain.entities.artigo import Artigo as ArtigoEntity
from app.domain.repositories.i_artigo_repository import IArtigoRepository
from app.infra.database import Base # Usamos o Base do nosso setup do DB

# 1. MODELO DA TABELA (DETALHE DE IMPLEMENTAÇÃO DO SQLALCHEMY)
# Este modelo representa a tabela 'artigos' no banco de dados.
class ArtigoModel(Base):
    __tablename__ = 'artigos'

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    ano = Column(Integer)
    doi = Column(String, unique=True, index=True, nullable=True)
    caminho_pdf = Column(String, nullable=True)
    # Adicionar outras colunas conforme a definição da sua tabela
    # id_edicao = Column(Integer, ForeignKey("edicoesevento.id"))


# 2. IMPLEMENTAÇÃO CONCRETA DO REPOSITÓRIO
class SQLiteArtigoRepository(IArtigoRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_entity(self, model: ArtigoModel) -> ArtigoEntity:
        """Converte um modelo SQLAlchemy para uma entidade de domínio."""
        return ArtigoEntity.from_orm(model)

    def find_by_titulo(self, titulo: str) -> List[ArtigoEntity]:
        """Encontra artigos por título, retornando uma lista de entidades."""
        query_result = self.db_session.query(ArtigoModel).filter(
            ArtigoModel.titulo.contains(titulo)
        ).all()
        return [self._to_entity(artigo) for artigo in query_result]
        
    def find_by_id(self, artigo_id: int) -> Optional[ArtigoEntity]:
        """Encontra um artigo pelo seu ID."""
        model = self.db_session.query(ArtigoModel).filter(ArtigoModel.id == artigo_id).first()
        if model:
            return self._to_entity(model)
        return None

    def save(self, artigo: ArtigoEntity) -> ArtigoEntity:
        """Salva um novo artigo ou atualiza um existente."""
        # Converte a entidade de domínio para um modelo do SQLAlchemy
        artigo_model = ArtigoModel(
            titulo=artigo.titulo,
            ano=artigo.ano,
            doi=artigo.doi,
            caminho_pdf=artigo.caminho_pdf
        )
        self.db_session.add(artigo_model)
        self.db_session.commit()
        self.db_session.refresh(artigo_model)
        return self._to_entity(artigo_model)