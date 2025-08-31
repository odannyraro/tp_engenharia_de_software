from typing import Optional
from pydantic import BaseModel, Field

class Autor(BaseModel):
    """
    Representa um autor de um artigo no domínio da aplicação.
    Um autor não é necessariamente um usuário do sistema.
    """
    id: Optional[int] = None
    nome: str = Field(..., min_length=3, description="Nome completo do autor")
    afiliacao: Optional[str] = Field(None, description="Afiliação institucional do autor")

    class Config:
        orm_mode = True # Habilita a compatibilidade com modelos ORM (SQLAlchemy)