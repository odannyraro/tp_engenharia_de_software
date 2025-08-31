from ..entities.artigo import Artigo
from ..repositories.i_artigo_repository import IArtigoRepository
from ..repositories.i_edicao_evento_repository import IEdicaoEventoRepository

class CadastrarArtigoUseCase:
    """
    Caso de uso para cadastrar um novo artigo manualmente.
    """
    def __init__(self, artigo_repository: IArtigoRepository, edicao_repository: IEdicaoEventoRepository):
        self.artigo_repository = artigo_repository
        self.edicao_repository = edicao_repository

    def execute(self, titulo: str, id_edicao: int) -> Artigo:
        """
        Executa o caso de uso.

        Args:
            titulo: O título do novo artigo.
            id_edicao: O ID da edição do evento onde o artigo foi publicado.

        Returns:
            A entidade do artigo criado.
            
        Raises:
            ValueError: Se a edição do evento informada não existir.
        """
        edicao = self.edicao_repository.find_by_id(id_edicao)
        if not edicao:
            raise ValueError(f"A edição com ID '{id_edicao}' não foi encontrada.")

        novo_artigo = Artigo(titulo=titulo, id_edicao=id_edicao)
        
        return self.artigo_repository.save(novo_artigo)