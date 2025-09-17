from pydantic import BaseModel, Field, EmailStr, AnyUrl
from typing import Optional

class UsuarioSchema(BaseModel):
    nome: str = Field(..., min_length=3, max_length=50, description="Nome Sobrenome")
    email: EmailStr
    senha: str = Field(..., min_length=5)
    admin: bool = False

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

    class Config:
        from_attribtes = True

class EventoSchema(BaseModel):
    """
    Representa um evento científico (ex: simpósio, conferência).
    """
    nome: str = Field(..., description="Nome completo do evento")
    sigla: Optional[str] = Field(None, description="Sigla do evento, ex: SBES")
    descricao: Optional[str] = Field(None, description="Breve descrição do evento")
    site: Optional[AnyUrl] = Field(None, description="URL do site oficial do evento")

    class Config:
        from_attributes = True

class EdicaoEventoSchema(BaseModel):
    """
    Representa uma edição específica de um evento científico em um determinado ano.
    """
    ano: int = Field(..., gt=1950, description="Ano de realização da edição")
    local: Optional[str] = Field(None, description="Local onde a edição ocorreu")
    id_evento: int = Field(..., description="ID do evento pai ao qual esta edição pertence")
    
    class Config:
        from_attributes = True

class ArtigoSchema(BaseModel):
    """
    Representa um artigo científico publicado em uma edição de um evento.
    """
    titulo: str = Field(..., min_length=5)
    autor: str = Field(..., description="Sobrenome, Nome")
    
    # Metadados de publicação (opcionais, comuns em BibTeX)
    journal: Optional[str] = None
    volume: Optional[str] = None
    numero: Optional[str] = None
    paginas: Optional[str] = None
    ano: Optional[int] = None
    publicador: Optional[str] = None
    doi: Optional[str] = Field(None, description="Valor unico")
    
    caminho_pdf: Optional[str] = Field(None, description="Caminho para o arquivo PDF armazenado")
    
    id_edicao: int = Field(..., description="ID da edição do evento onde o artigo foi publicado")
    
    # Relacionamento: um artigo pode ter vários autores
    #autores: List[Autor] = []

    class Config:
        from_attributes = True

class ResponseArtigoSchema(BaseModel):
    titulo: str
    autor: str
    caminho_pdf: str
    journal: str
    ano: int
    id_edicao: int

    class Config:
        from_attributes = True