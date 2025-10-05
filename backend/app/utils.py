import bibtexparser
from bibtexparser.customization import convert_to_unicode
from schemas import ArtigoSchema  # Assumindo que schemas é importável
from typing import List # Novo import necessário para o tipo de retorno

# A função agora retorna uma lista de ArtigoSchema
def parse_bibtex_to_artigo_schema(bibtex_text: str):
    from bibtexparser import loads
    bib_database = loads(bibtex_text)
    
    artigos = []
    for entry in bib_database.entries:
        chave = entry.get("ID") or entry.get("key")  # "sbes-paper3"
        
        artigo = ArtigoSchema(
            titulo=entry.get("title"),
            autores=entry.get("author"),
            nome_evento=entry.get("booktitle"),
            ano=int(entry["year"]) if "year" in entry else None,
            pagina_inicial=int(entry["pages"].split("--")[0]) if "pages" in entry and "--" in entry["pages"] else None,
            pagina_final=int(entry["pages"].split("--")[1]) if "pages" in entry and "--" in entry["pages"] else None,
            caminho_pdf=None,
            booktitle=entry.get("booktitle"),
            publisher=entry.get("publisher"),
            location=entry.get("location"),
        )

        artigos.append((artigo, chave))  # ✅ retorna a chave junto

    return artigos

    """
    Realiza o parsing de uma string BibTeX com múltiplas entradas
    e mapeia CADA entrada para um objeto ArtigoSchema, exigindo apenas o TÍTULO.
    """
    
    # 1. Parsing da string BibTeX
    try:
        parser = bibtexparser.bparser.BibTexParser(
            customization=convert_to_unicode,
            ignore_nonstandard_types=False
        )
        bib_database = bibtexparser.loads(bibtex_data, parser=parser)
        
    except Exception as e:
        raise ValueError(f"O formato da string BibTeX é inválido: {e}")

    entries = bib_database.entries
    
    if not entries:
        raise ValueError("Nenhuma entrada de artigo (entry) válida foi encontrada na string BibTeX.")
        
    artigos_list = []
    
    # Itera sobre TODAS as entradas (artigos) encontradas
    for entry in entries:
        
        # 2. Validação e Extração de Campos
        entry_id = entry.get('ID', 'N/A')
        
        # O ÚNICO CAMPO OBRIGATÓRIO: TITLE (título)
        if 'title' not in entry:
            raise ValueError(f"O campo obrigatório 'title' está faltando na entrada BibTeX (Key: {entry_id}).")

        # --- Campos Opcionais ---
        
        # Autores: Usa 'N/A' se estiver faltando
        autores = entry.get('author', 'N/A').strip()
        
        # Ano: Tenta converter para int, usa None se faltar ou falhar na conversão
        ano = entry.get('year')
        if ano:
            try:
                ano = int(ano.strip())
            except ValueError:
                ano = None # Falha na conversão
        
        # Nome do Evento (usado para buscar EdicaoEvento e Evento no BD)
        nome_evento = entry.get('booktitle') or entry.get('journal') or entry.get('publisher')
        
        # Se nome_evento for crítico para o seu BD (como a validação no router exige),
        # é mais seguro usar 'N/A' ou um valor padrão, mas notificar o usuário que 
        # ele precisa corrigir no BD depois, pois o router precisa desse campo para validar a edição.
        nome_evento_clean = nome_evento.strip() if nome_evento else 'N/A' 


        # 3. Criação do ArtigoSchema
        try:
            artigo_schema_data = ArtigoSchema(
                # Campos essenciais
                titulo=entry['title'].strip(),
                autores=autores,
                nome_evento=nome_evento_clean,
                ano=ano, # Pode ser int ou None
                
                # Campos opcionais
                pagina_inicial=entry.get('pages', '').split('--')[0].strip() if entry.get('pages') else entry.get('page_start'),
                pagina_final=entry.get('pages', '').split('--')[-1].strip() if entry.get('pages') and '--' in entry['pages'] else entry.get('page_end'),
                caminho_pdf=entry.get('url') or entry.get('file'), 
                booktitle=entry.get('booktitle'),
                publisher=entry.get('publisher'),
                location=entry.get('address') or entry.get('location')
            )
            # Adiciona o ArtigoSchema válido à lista
            artigos_list.append(artigo_schema_data)
            
        except Exception as e:
            # Erro de Pydantic/conversão (improvável com os checks acima, mas seguro)
            raise ValueError(f"Erro inesperado ao criar ArtigoSchema na entrada {entry_id}: {e}")

    return artigos_list