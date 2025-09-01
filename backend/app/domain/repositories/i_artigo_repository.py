from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.artigo import Artigo

class IArtigoRepository(ABC):
    """Interface para o repositório de Artigos."""

    @abstractmethod
    def save(self, artigo: Artigo) -> Artigo:
        """Salva um artigo."""
        pass

    @abstractmethod
    def find_by_id(self, artigo_id: int) -> Optional[Artigo]:
        """Encontra um artigo pelo seu ID."""
        pass

    @abstractmethod
    def find_by_titulo(self, titulo: str) -> List[Artigo]:
        """Encontra artigos que contenham a string no título."""
        pass

    @abstractmethod
    def find_by_autor_id(self, autor_id: int) -> List[Artigo]:
        """Encontra todos os artigos de um determinado autor."""
        pass
        
    @abstractmethod
    def find_by_edicao_id(self, edicao_id: int) -> List[Artigo]:
        """Encontra todos os artigos de uma edição de evento."""
        pass

    @abstractmethod
    def find_all(self) -> List[Artigo]:
        """Retorna todos os artigos."""
        pass
    
    @abstractmethod
    def delete(self, artigo_id: int) -> None:
        """Deleta um artigo pelo seu ID."""
        pass