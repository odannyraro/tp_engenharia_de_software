from typing import List
from ..entities.artigo import Artigo
from ..repositories.i_artigo_repository import IArtigoRepository

class PesquisarArtigoUseCase:
    def __init__(self, artigo_repository: IArtigoRepository):
        self.artigo_repository = artigo_repository

    def execute(self, titulo: str) -> List[Artigo]:
        if not titulo or len(titulo) < 3:
            raise ValueError("O título para pesquisa deve ter pelo menos 3 caracteres.")
        
        return self.artigo_repository.find_by_titulo(titulo)