from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.domain.entities.artigo import Artigo
from app.domain.use_cases.pesquisar_artigo import PesquisarArtigoUseCase
from app.domain.repositories.i_artigo_repository import IArtigoRepository
from app.infra.dependencies import get_artigo_repository

router = APIRouter(
    prefix="/artigos",
    tags=["Artigos"]
)

@router.get("/", response_model=List[Artigo])
def pesquisar_artigos(
    titulo: str,
    repo: IArtigoRepository = Depends(get_artigo_repository)
):
    try:
        use_case = PesquisarArtigoUseCase(repo)
        artigos = use_case.execute(titulo)
        return artigos
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))