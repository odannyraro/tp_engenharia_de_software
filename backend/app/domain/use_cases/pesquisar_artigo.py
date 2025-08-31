from typing import List
from ..entities.artigo import Artigo
from ..repositories.i_artigo_repository import IArtigoRepository
from ..repositories.i_evento_repository import IEventoRepository

class PesquisarArtigosUseCase:
    """
    Caso de uso para pesquisar artigos por diferentes critérios.
    """
    def __init__(self, artigo_repository: IArtigoRepository, evento_repository: IEventoRepository):
        self.artigo_repository = artigo_repository
        self.evento_repository = evento_repository

    def por_titulo(self, titulo: str) -> List[Artigo]:
        """Busca artigos por título."""
        if not titulo or len(titulo) < 3:
            raise ValueError("O título para pesquisa deve ter pelo menos 3 caracteres.")
        return self.artigo_repository.find_by_titulo(titulo)

    def por_nome_evento(self, nome_evento: str) -> List[Artigo]:
        """Busca artigos por nome do evento (função simplificada)."""
        # Em um caso real, a busca seria mais elaborada, envolvendo múltiplos repositórios.
        # Esta é uma implementação simples para ilustrar o conceito.
        eventos = self.evento_repository.find_by_nome(nome_evento)
        if not eventos:
            return []
        
        # Lógica para buscar artigos de todas as edições desses eventos
        # ... (deixado como exercício)
        return [] # Retorno placeholder