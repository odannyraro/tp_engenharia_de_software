from pydantic import BaseModel, Field
from typing import Optional

class Artigo(BaseModel):
    id: Optional[int] = None
    titulo: str = Field(min_length=3)
    ano: Optional[int] = Field(None, gt=1900)
    doi: Optional[str] = None
    caminho_pdf: Optional[str] = None

    class Config:
        orm_mode = True # Permite que o modelo seja criado a partir de um objeto ORM