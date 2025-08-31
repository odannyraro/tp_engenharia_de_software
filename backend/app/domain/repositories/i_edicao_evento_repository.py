# File: backend/app/domain/repositories/i_edicao_evento_repository.py

from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.edicao_evento import EdicaoEvento

class IEdicaoEventoRepository(ABC):
    """Interface para o repositório de Edições de Eventos."""

    @abstractmethod
    def save(self, edicao_evento: EdicaoEvento) -> EdicaoEvento:
        """Salva uma edição de evento."""
        pass

    @abstractmethod
    def find_by_id(self, edicao_id: int) -> Optional[EdicaoEvento]:
        """Encontra uma edição de evento pelo seu ID."""
        pass

    @abstractmethod
    def find_by_evento_id(self, evento_id: int) -> List[EdicaoEvento]:
        """Encontra todas as edições de um determinado evento."""
        pass

    @abstractmethod
    def delete(self, edicao_id: int) -> None:
        """Deleta uma edição de evento pelo seu ID."""
        pass