from fastapi import Depends
from sqlalchemy.orm import Session

from .database import get_db
from app.adapters.repositories.sqlite_artigo_repository import SQLiteArtigoRepository
from app.domain.repositories.i_artigo_repository import IArtigoRepository

def get_artigo_repository(db: Session = Depends(get_db)) -> IArtigoRepository:
    return SQLiteArtigoRepository(db)