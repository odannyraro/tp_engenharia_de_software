# File: backend/app/adapters/api/artigo_router.py

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from typing import List
from sqlalchemy.exc import IntegrityError 

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
    try:
        novo_artigo = repo.save(artigo_data)
        return novo_artigo
    # Captura a exceção específica de violação de integridade (como a de chave única)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # <-- Código de status mais apropriado
            detail="Um artigo com este DOI já existe."
        )
    except Exception as e:
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
    

from app.domain.repositories.i_artigo_repository import IArtigoRepository
from app.infra.dependencies import get_artigo_repository
from app.domain.use_cases.importar_bibtex import ImportarBibTeX 

@router.post("/importar-bibtex")
async def importar_bibtex(
    arquivo: UploadFile = File(...),
    # 1. Injetar o repositório
    repo: IArtigoRepository = Depends(get_artigo_repository) 
):
    """
    Importa vários artigos a partir de um arquivo BibTeX.
    Apenas administradores podem usar.
    """
    if not arquivo.filename.endswith(".bib"):
        raise HTTPException(status_code=400, detail="O arquivo deve ter extensão .bib")

    try:
        conteudo = await arquivo.read()
        conteudo_str = conteudo.decode("utf-8")
        
        # 2. Instanciar o Caso de Uso com a dependência (o repositório)
        use_case = ImportarBibTeX(artigo_repository=repo)
        
        # 3. Chamar o método do Caso de Uso, movendo a lógica de negócio para a camada Domain
        qtd = use_case.importar_artigos_bibtex(conteudo_str)
        
        return {"mensagem": f"{qtd} artigos importados com sucesso."}
    
    # 4. Tratar possíveis erros de parse, banco de dados, etc.
    except Exception as e:
        # Você pode adicionar tratamento mais específico aqui, como IntegrityError
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao importar artigos: {e}"
        )