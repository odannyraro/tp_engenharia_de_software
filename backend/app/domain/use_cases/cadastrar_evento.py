from ..entities.evento import Evento
from ..repositories.i_evento_repository import IEventoRepository

class CadastrarEventoUseCase:
    """
    Caso de uso para cadastrar um novo evento científico.
    """
    def __init__(self, evento_repository: IEventoRepository):
        self.evento_repository = evento_repository

    def execute(self, nome: str, sigla: str) -> Evento:
        """
        Executa o caso de uso.

        Args:
            nome: O nome do novo evento.
            sigla: A sigla do novo evento.

        Returns:
            A entidade do evento que foi criada.

        Raises:
            ValueError: Se um evento com a mesma sigla já existir.
        """
        evento_existente = self.evento_repository.find_by_sigla(sigla)
        if evento_existente:
            raise ValueError(f"Já existe um evento cadastrado com a sigla '{sigla}'.")

        novo_evento = Evento(nome=nome, sigla=sigla)
        
        return self.evento_repository.save(novo_evento)