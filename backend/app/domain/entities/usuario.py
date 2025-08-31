from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class Usuario(BaseModel):
    """
    Representa um usuário cadastrado no sistema da biblioteca digital.
    """
    id: Optional[int] = None
    nome: str = Field(..., min_length=3)
    email: EmailStr
    
    # A senha nunca deve ser retornada em respostas de API.
    # Em um projeto real, usariamos schemas separados para entrada e saída.
    senha: str = Field(..., min_length=6, description="A senha deve ser armazenada como um hash")
    
    ehAdmin: bool = Field(False, description="Indica se o usuário é um administrador")

    class Config:
        orm_mode = True