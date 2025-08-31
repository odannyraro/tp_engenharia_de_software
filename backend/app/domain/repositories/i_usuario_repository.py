from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.usuario import Usuario

class IUsuarioRepository(ABC):
    """Interface para o repositório de Usuários."""

    @abstractmethod
    def save(self, usuario: Usuario) -> Usuario:
        """Salva um usuário."""
        pass

    @abstractmethod
    def find_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """Encontra um usuário pelo seu ID."""
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Usuario]:
        """Encontra um usuário pelo seu e-mail."""
        pass

    @abstractmethod
    def find_all(self) -> List[Usuario]:
        """Retorna todos os usuários."""
        pass

    @abstractmethod
    def delete(self, usuario_id: int) -> None:
        """Deleta um usuário pelo seu ID."""
        pass