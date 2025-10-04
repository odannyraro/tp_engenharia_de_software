
from ..entities.artigo import Artigo
from ..repositories.i_artigo_repository import IArtigoRepository
from bibtexparser import loads

class ImportarBibTeX:
    """
    Caso de uso para importar artigos a partir de um arquivo BibTeX.
    """
    def __init__(self, artigo_repository: IArtigoRepository):
        self.artigo_repository = artigo_repository
        
    def importar_artigos_bibtex(self, conteudo_bibtex: str) -> int:
        """
        Faz o parse do arquivo BibTeX e cadastra os artigos.
        Retorna a quantidade de artigos importados.
        """
        data = loads(conteudo_bibtex)
        count = 0
        # O ID_EDICAO_IMPORTACAO é necessário para satisfazer o campo obrigatório.
        ID_EDICAO_IMPORTACAO = 0 

        for entry in data.entries:
            titulo = entry.get("title", "").strip("{}")
            autores_str = entry.get("author", "")
            ano = entry.get("year", "")
            doi = entry.get("doi", "")
            journal = entry.get("journal", "")
            volume = entry.get("volume", "")
            numero = entry.get("number", "")
            paginas = entry.get("pages", "")

            # --- 1. PREPARAÇÃO DO CAMPO 'autores' (Lista de Objetos) ---
            autores_list_para_artigo = []
            if autores_str:
                # Extrai apenas o primeiro autor da string
                primeiro_autor_nome = autores_str.split(' and ')[0].strip()
                
                if primeiro_autor_nome:
                    # Cria o dicionário/objeto placeholder para satisfazer a validação List[Autor].
                    # O seu modelo Artigo espera uma Lista de Objetos/Dicionários com o campo 'nome'.
                    autor_placeholder = {"nome": primeiro_autor_nome}
                    autores_list_para_artigo.append(autor_placeholder)

            # --- 2. PREPARAÇÃO DO CAMPO 'autores_texto' (String Completa) ---
            # Este campo armazena todos os autores separados por vírgula.
            autores_texto = autores_str.replace(' and ', ', ')
            autores_texto = autores_texto.strip()
            
            # --- 3. CRIAÇÃO E SALVAMENTO DA ENTIDADE ---
            if titulo:
                # O Artigo DEVE ter o campo 'autores_texto' para esta lógica funcionar
                artigo = Artigo(
                    titulo=titulo,
                    autores=autores_list_para_artigo,  # Lista de objetos/dicionários (para validação)
                    autores_texto=autores_texto,       # String completa (para exibição/busca)
                    ano=ano,
                    doi=doi,
                    id_edicao=ID_EDICAO_IMPORTACAO,
                    journal=journal,
                    volume=volume,
                    numero=numero,
                    paginas=paginas,
                )
                
                self.artigo_repository.save(artigo)
                count += 1

        return count