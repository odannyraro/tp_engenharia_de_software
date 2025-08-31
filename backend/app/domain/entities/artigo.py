from typing import List, Optional
from pydantic import BaseModel, Field
from .autor import Autor # Importação relativa da entidade Autor

class Artigo(BaseModel):
    """
    Representa um artigo científico publicado em uma edição de um evento.
    """
    id: Optional[int] = None
    titulo: str = Field(..., min_length=5)
    
    # Metadados de publicação (opcionais, comuns em BibTeX)
    journal: Optional[str] = None
    volume: Optional[str] = None
    numero: Optional[str] = None
    paginas: Optional[str] = None
    ano: Optional[int] = None
    publicador: Optional[str] = None
    doi: Optional[str] = None
    
    caminho_pdf: Optional[str] = Field(None, description="Caminho para o arquivo PDF armazenado")
    
    id_edicao: int = Field(..., description="ID da edição do evento onde o artigo foi publicado")
    
    # Relacionamento: um artigo pode ter vários autores
    autores: List[Autor] = []

    class Config:
        orm_mode = True