from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.evento import Evento

class IEventoRepository(ABC):
    """Interface para o repositório de Eventos."""

    @abstractmethod
    def save(self, evento: Evento) -> Evento:
        """Salva um evento (cria um novo ou atualiza um existente)."""
        pass

    @abstractmethod
    def find_by_id(self, evento_id: int) -> Optional[Evento]:
        """Encontra um evento pelo seu ID."""
        pass

    @abstractmethod
    def find_by_sigla(self, sigla: str) -> Optional[Evento]:
        """Encontra um evento pela sua sigla (ex: 'SBES')."""
        pass
    
    @abstractmethod
    def find_by_nome(self, nome: str) -> List[Evento]:
        """Encontra eventos por nome."""
        pass

    @abstractmethod
    def find_all(self) -> List[Evento]:
        """Retorna todos os eventos cadastrados."""
        pass

    @abstractmethod
    def delete(self, evento_id: int) -> None:
        """Deleta um evento pelo seu ID."""
        pass