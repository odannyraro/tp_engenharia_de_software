from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.artigo import Artigo

class IArtigoRepository(ABC):

    @abstractmethod
    def find_by_titulo(self, titulo: str) -> List[Artigo]:
        """Encontra artigos por título."""
        pass

    @abstractmethod
    def save(self, artigo: Artigo) -> Artigo:
        """Salva um novo artigo ou atualiza um existente."""
        pass