from typing import List, Dict
from ..entities.artigo import Artigo
from ..repositories.i_artigo_repository import IArtigoRepository
from ..repositories.i_autor_repository import IAutorRepository

class ListarArtigosDeAutorUseCase:
    """
    Caso de uso para listar os artigos de um autor específico.
    """
    def __init__(self, artigo_repository: IArtigoRepository, autor_repository: IAutorRepository):
        self.artigo_repository = artigo_repository
        self.autor_repository = autor_repository

    def execute(self, autor_id: int) -> Dict[int, List[Artigo]]:
        """
        Executa o caso de uso.

        Args:
            autor_id: O ID do autor.

        Returns:
            Um dicionário com os artigos do autor, agrupados por ano de publicação.
            Ex: {2025: [artigo1, artigo2], 2024: [artigo3]}
        
        Raises:
            ValueError: Se o autor não for encontrado.
        """
        autor = self.autor_repository.find_by_id(autor_id)
        if not autor:
            raise ValueError(f"Autor com ID {autor_id} não encontrado.")

        artigos = self.artigo_repository.find_by_autor_id(autor_id)
        
        # Organiza os artigos por ano
        artigos_por_ano = {}
        for artigo in artigos:
            if artigo.ano:
                if artigo.ano not in artigos_por_ano:
                    artigos_por_ano[artigo.ano] = []
                artigos_por_ano[artigo.ano].append(artigo)
        
        return artigos_por_ano