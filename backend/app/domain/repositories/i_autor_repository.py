from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.autor import Autor

class IAutorRepository(ABC):
    """Interface para o repositório de Autores."""

    @abstractmethod
    def save(self, autor: Autor) -> Autor:
        """Salva um autor."""
        pass

    @abstractmethod
    def find_by_id(self, autor_id: int) -> Optional[Autor]:
        """Encontra um autor pelo seu ID."""
        pass

    @abstractmethod
    def find_by_name(self, nome: str) -> Optional[Autor]:
        """Encontra um autor pelo nome (útil para evitar duplicatas)."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Autor]:
        """Retorna todos os autores."""
        pass