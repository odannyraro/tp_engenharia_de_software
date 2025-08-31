# File: backend/app/adapters/api/artigo_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

# Importações da Arquitetura Limpa
from app.domain.entities.artigo import Artigo as ArtigoEntity
from app.domain.repositories.i_artigo_repository import IArtigoRepository
from app.infra.dependencies import get_artigo_repository

# Casos de Uso (a serem criados na pasta domain/use_cases)
# from app.domain.use_cases.pesquisar_artigo_use_case import PesquisarArtigoUseCase
# from app.domain.use_cases.cadastrar_artigo_use_case import CadastrarArtigoUseCase

# --- SCHEMAS (Data Transfer Objects) ---
# Usamos Pydantic para definir os formatos de entrada e saída da API.
# Neste caso, podemos reutilizar a nossa entidade, mas é uma boa prática
# ter schemas separados para desacoplar a API do modelo de domínio.

class ArtigoCreateSchema(ArtigoEntity):
    # O ID será gerado pelo banco, então o removemos do schema de criação
    id: None = None

class ArtigoResponseSchema(ArtigoEntity):
    id: int # Na resposta, garantimos que o ID estará presente

# --- ROUTER ---
router = APIRouter(
    prefix="/artigos",
    tags=["Artigos"]
)

@router.post("/", response_model=ArtigoResponseSchema, status_code=status.HTTP_201_CREATED)
def cadastrar_artigo(
    artigo_data: ArtigoCreateSchema,
    repo: IArtigoRepository = Depends(get_artigo_repository)
):
    """
    Endpoint para cadastrar um novo artigo. 
    """
    try:
        # Em uma implementação completa, aqui chamaríamos o Use Case:
        # use_case = CadastrarArtigoUseCase(repo)
        # novo_artigo = use_case.execute(artigo_data)
        
        # Implementação simplificada diretamente no router:
        novo_artigo = repo.save(artigo_data)
        return novo_artigo
    except Exception as e:
        # Em um caso real, trataríamos exceções específicas (ex: DOI duplicado)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao cadastrar artigo: {e}"
        )

@router.get("/", response_model=List[ArtigoResponseSchema])
def pesquisar_artigos(
    titulo: str,
    repo: IArtigoRepository = Depends(get_artigo_repository)
):
    """
    Endpoint para pesquisar artigos por título. 
    """
    try:
        # Em uma implementação completa, aqui chamaríamos o Use Case:
        # use_case = PesquisarArtigoUseCase(repo)
        # artigos = use_case.execute(titulo)
        
        # Implementação simplificada diretamente no router:
        artigos = repo.find_by_titulo(titulo)
        if not artigos:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum artigo encontrado com o título fornecido."
            )
        return artigos
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))