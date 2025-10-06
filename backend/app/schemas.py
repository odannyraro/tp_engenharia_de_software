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
    entidade_promotora: Optional[str] = Field(None, description="Entidade promotora do evento")

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
    @classmethod
    def as_form(
        cls,
        titulo: str = Field(..., min_length=5),
        autores: str = Field(..., description="Nomes completos dos autores separados por ' and '"),
        nome_evento: str = Field(..., description="Nome do evento onde o artigo foi publicado"),
        ano: Optional[int] = None,
        pagina_inicial: Optional[int] = None,
        pagina_final: Optional[int] = None,
        caminho_pdf: Optional[str] = None,
        booktitle: Optional[str] = None,
        publisher: Optional[str] = None,
        location: Optional[str] = None,
    ):
        return cls(
            titulo=titulo,
            autores=autores,
            nome_evento=nome_evento,
            ano=ano,
            pagina_inicial=pagina_inicial,
            pagina_final=pagina_final,
            caminho_pdf=caminho_pdf,
            booktitle=booktitle,
            publisher=publisher,
            location=location,
        )
    """
    Representa um artigo científico publicado em uma edição de um evento.
    """
    titulo: str = Field(..., min_length=5)
    autores: str = Field(..., description="Nomes completos dos autores separados por ' and '")
    nome_evento: str = Field(..., description="Nome do evento onde o artigo foi publicado")
    ano: Optional[int] = None
    pagina_inicial: Optional[int] = None
    pagina_final: Optional[int] = None
    caminho_pdf: Optional[str] = Field(None, description="Caminho para o arquivo PDF armazenado")
    booktitle: Optional[str] = None
    publisher: Optional[str] = None
    location: Optional[str] = None
    
    # Relacionamento: um artigo pode ter vários autores
    #autores: List[Autor] = []

    class Config:
        from_attributes = True

class ResponseArtigoSchema(BaseModel):
    id: Optional[int] = None
    titulo: str
    autores: str
    nome_evento: str
    ano: Optional[int]
    pagina_inicial: Optional[int]
    pagina_final: Optional[int]
    caminho_pdf: Optional[str]
    booktitle: Optional[str]
    publisher: Optional[str]
    location: Optional[str]
    id_edicao: Optional[int]

    class Config:
        from_attributes = True


class SubscriberSchema(BaseModel):
    nome: str = Field(..., description="Nome do assinante, ex: Silva, Pedro ou Pedro Silva")
    email: EmailStr

    class Config:
        from_attributes = True


class ResponseSubscriberSchema(BaseModel):
    id: int
    nome: str
    email: EmailStr

    class Config:
        from_attributes = True


class BibtexImportSchema(BaseModel):
    bibtex_data: str