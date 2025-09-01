from typing import Optional
from pydantic import BaseModel, Field, AnyUrl

class Evento(BaseModel):
    """
    Representa um evento científico (ex: simpósio, conferência).
    """
    id: Optional[int] = None
    nome: str = Field(..., description="Nome completo do evento")
    sigla: Optional[str] = Field(None, description="Sigla do evento, ex: SBES")
    descricao: Optional[str] = Field(None, description="Breve descrição do evento")
    site_oficial: Optional[AnyUrl] = Field(None, description="URL do site oficial do evento")

    class Config:
        from_attributes = True